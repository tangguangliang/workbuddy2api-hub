#!/usr/bin/env python3
"""Diagnose the upstream `11-128` channel check ("Illegal API invocation from an
unapproved channel") for a client's system prompt, and shrink it to a minimal
trigger.

为什么需要它：上游对「非官方客户端」的识别是**累积式**的，一条提示词里任意两
段措辞凑在一起就可能命中，而单句分别发送都是 200。手工排查要反复构造请求、二
分、记录结果；这个脚本把同一套流程固定下来，三分钟出结论。

流程（每一步都可以单独执行）：

  1. 取提示词：`--session` 直接解 DSH 会话日志里的系统提示词，或 `--file` / `--stdin`；
  2. 复现：整段按 `--role`（默认 system）发一次，确认确实 400 / 11-128；
  3. 段落扫描：逐段累加前缀，找出第一个开始被拦的段落；
  4. 收缩：句子级 → 二分，找到「整段被拦、两半都放行」的最小连续窗口；
  5. 顺带给出可复制的下一步：改窗口里的一个词，再用 `--check` 验证。

用法示例：

    # 解最近的 DSH 会话并定位
    python scripts/diagnose_11_128.py --session latest

    # 已经有一份提示词文本
    python scripts/diagnose_11_128.py --file prompt.txt --role system

    # 验证一条改写是否放行（返回 0 = 放行）
    python scripts/diagnose_11_128.py --check "Tokens prefixed with @ are paths the user explicitly mentioned."

    # 机器可读
    python scripts/diagnose_11_128.py --session latest --json

成本：每条探针都是一次真实上游请求（max_tokens=4，整段提示词约 1.5k token），
默认 `--max-calls 40` 封顶；命中后立刻停止，不会跑满。

退出码：0 复现并定位成功（或 `--check` 通过）；1 未能复现 / 探针异常；
2 用法或环境问题（找不到 Key、读不到会话等）。
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BASE = os.environ.get("WB_PROXY_URL") or "http://127.0.0.1:8788"
DEFAULT_MODEL = os.environ.get("WB_PROBE_MODEL") or "deepseek-v4.1-flash"
SESSION_ROOT = os.path.join(os.path.expanduser("~"), ".dsh", "sessions")
MAX_TOKENS = 4


# --------------------------------------------------------------------------
# 输入：提示词
# --------------------------------------------------------------------------

def _unzstd(path):
    """解一份 .zstd 文件，返回 utf-8 文本。

    Python 3.9 的标准库没有 zstd，所以按可用性降级：`zstandard` 模块 →
    `zstd` 命令行 → `node`（22+ 的 zlib.zstdDecompressSync）。三条都没有时
    给出可执行的提示，不静默返回空串。
    """
    try:
        import zstandard  # noqa: F401  (可选依赖)
        with open(path, "rb") as fh:
            return zstandard.ZstdDecompressor().stream_reader(fh).read().decode(
                "utf-8", "replace")
    except ImportError:
        pass
    try:
        done = subprocess.run(["zstd", "-dc", path], capture_output=True)
        if done.returncode == 0:
            return done.stdout.decode("utf-8", "replace")
    except OSError:
        pass
    try:
        out = os.path.join(tempfile.gettempdir(), "wb-unzstd-%d.txt" % os.getpid())
        snippet = ("const fs=require('fs'),z=require('zlib');"
                   "fs.writeFileSync(process.argv[2],"
                   "z.zstdDecompressSync(fs.readFileSync(process.argv[1])))")
        done = subprocess.run(["node", "-e", snippet, path, out],
                              capture_output=True)
        if done.returncode == 0 and os.path.exists(out):
            with open(out, "rb") as fh:
                text = fh.read().decode("utf-8", "replace")
            os.remove(out)
            return text
    except OSError:
        pass
    raise RuntimeError(
        "cannot decompress %s: install the `zstandard` module, or put `zstd` / `node` "
        "on PATH, or pass the prompt with --file" % os.path.basename(path))


def newest_session():
    """本机上最近写入的 session.v4.jsonl.zstd 路径。"""
    pattern = os.path.join(SESSION_ROOT, "*", "*", "session.v4.jsonl.zstd")
    files = glob.glob(pattern)
    if not files:
        raise RuntimeError("no DSH session log under %s" % SESSION_ROOT)
    return max(files, key=os.path.getmtime)


def system_prompt_from_session(path):
    """从会话日志里取最后一条 system/message 的正文（就是客户端发出去的那份）。"""
    text = _unzstd(path)
    found = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("type") != "system/message":
            continue
        parts = ((row.get("data") or {}).get("message") or {}).get("content") or []
        body = "".join(p.get("text") or "" for p in parts if isinstance(p, dict))
        if body:
            found = body
    if not found:
        raise RuntimeError("no system/message record in %s" % path)
    return found


def read_prompt(args):
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            return fh.read()
    if args.stdin:
        return sys.stdin.read()
    session = args.session
    if session in (None, "latest"):
        session = newest_session()
    elif os.path.isdir(session):
        candidate = os.path.join(session, "session.v4.jsonl.zstd")
        session = candidate if os.path.exists(candidate) else newest_session()
    return system_prompt_from_session(session)


# --------------------------------------------------------------------------
# 探针
# --------------------------------------------------------------------------

def api_key(explicit=None):
    if explicit:
        return explicit
    env = os.environ.get("WB_API_KEY") or os.environ.get("WB_PROXY_API_KEY")
    if env:
        return env.strip()
    settings = os.path.join(ROOT, "accounts", "settings.json")
    try:
        with open(settings, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return ""
    keys = [k for k in (data.get("api_keys") or [])
            if isinstance(k, dict) and k.get("enabled") and k.get("key")]
    for name in ("local", "LAN"):
        for k in keys:
            if k.get("name") == name:
                return k["key"]
    return keys[0]["key"] if keys else ""


class Probe(object):
    """一次上游探针：返回 True 表示被 11-128 拦下。"""

    def __init__(self, base_url, key, role="system", model=DEFAULT_MODEL,
                 timeout=120, max_calls=40, quiet=False):
        self.url = base_url.rstrip("/")
        if not self.url.endswith("/v1"):
            self.url += "/v1"
        self.key = key
        self.role = role
        self.model = model
        self.timeout = timeout
        self.max_calls = max_calls
        self.calls = 0
        self.quiet = quiet

    def blocked(self, text):
        if self.calls >= self.max_calls:
            raise RuntimeError("probe budget exhausted (%d calls); raise --max-calls"
                               % self.max_calls)
        self.calls += 1
        messages = [{"role": self.role, "content": text},
                    {"role": "user", "content": "hi"}]
        body = json.dumps({"model": self.model, "max_tokens": MAX_TOKENS,
                           "messages": messages}).encode("utf-8")
        req = urllib.request.Request(
            self.url + "/chat/completions", data=body, method="POST",
            headers={"content-type": "application/json",
                     "authorization": "Bearer " + self.key})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp.read()
                hit = False
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            hit = ("11-128" in raw) or ("unapproved" in raw)
            if not hit and exc.code >= 500:
                raise RuntimeError("upstream error %d: %s" % (exc.code, raw[:200]))
        if not self.quiet:
            print("    #%02d %-7s %4d chars  %s"
                  % (self.calls, "BLOCKED" if hit else "ok", len(text),
                     _head(text)))
        return hit


def _head(text, limit=60):
    one = re.sub(r"\s+", " ", text).strip()
    return one[:limit] + ("…" if len(one) > limit else "")


# --------------------------------------------------------------------------
# 二分
# --------------------------------------------------------------------------

def split_paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def first_blocking_prefix(paragraphs, blocked):
    """逐段累加，返回第一个开始被拦的「段数」（1 起），没有则 0。"""
    for i in range(1, len(paragraphs) + 1):
        if blocked("\n\n".join(paragraphs[:i])):
            return i
    return 0


def _halves(text):
    mid = len(text) // 2
    cut = text.rfind(" ", 0, mid)
    if cut < 40:
        cut = mid
    return text[:cut], text[cut:].lstrip()


def shrink(text, blocked, max_rounds=30):
    """把阻塞文本收缩到「整段被拦、两半都放行」的最小连续窗口。

    累积式指纹没有单点触发，所以返回的是**最小窗口**而不是单个短语：
    窗口内任意一段都可能是信号之一，改其中一处即可破局。
    """
    windows = []
    queue = [text]
    rounds = 0
    while queue and rounds < max_rounds:
        rounds += 1
        current = queue.pop(0)
        left, right = _halves(current)
        if not left.strip() or not right.strip():
            windows.append(current)
            continue
        hit_left = blocked(left)
        hit_right = blocked(right)
        if not hit_left and not hit_right:
            windows.append(current)          # 断裂点就在这两半之间
            continue
        if hit_left:
            queue.append(left)
        if hit_right:
            queue.append(right)
    return windows


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="定位上游 11-128 渠道校验的触发文本（累积式指纹，二分收缩）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--session", nargs="?", const="latest",
                     help="DSH 会话目录或 .zstd 文件；省略值 = 最近一次会话")
    src.add_argument("--file", help="直接给一份提示词文本")
    src.add_argument("--stdin", action="store_true", help="从标准输入读提示词")
    ap.add_argument("--check", metavar="TEXT",
                    help="只验证一段文本是否放行（返回 0 = 放行）")
    ap.add_argument("--base-url", default=DEFAULT_BASE, help="网关地址，默认 %(default)s")
    ap.add_argument("--api-key", help="覆盖 API Key（默认取 accounts/settings.json）")
    ap.add_argument("--role", default="system",
                    choices=("system", "developer", "user"),
                    help="探针使用的消息角色，默认 system（上游对 system 最敏感）")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--max-calls", type=int, default=40, help="探针上限，默认 %(default)s")
    ap.add_argument("--timeout", type=int, default=120, help="单次请求超时秒数")
    ap.add_argument("--json", action="store_true", help="输出机器可读结果")
    ap.add_argument("--quiet", action="store_true", help="不打印每条探针")
    args = ap.parse_args(argv)

    key = api_key(args.api_key)
    if not key:
        print("no API key: pass --api-key or add one in the panel", file=sys.stderr)
        return 2
    probe = Probe(args.base_url, key, role=args.role, model=args.model,
                  timeout=args.timeout, max_calls=args.max_calls, quiet=args.quiet)

    if args.check:
        try:
            hit = probe.blocked(args.check)
        except RuntimeError as exc:
            print("probe failed: %s" % exc, file=sys.stderr)
            return 1
        print("verdict: %s" % ("BLOCKED (11-128)" if hit else "PASSES"))
        return 0 if not hit else 1

    if not (args.session or args.file or args.stdin):
        ap.print_help()
        return 2
    try:
        prompt = read_prompt(args)
    except (OSError, RuntimeError) as exc:
        print("cannot read prompt: %s" % exc, file=sys.stderr)
        return 2
    if not prompt.strip():
        print("prompt is empty", file=sys.stderr)
        return 2

    started = time.time()
    if not args.quiet and not args.json:
        print("prompt: %d chars, role=%s, model=%s" % (len(prompt), args.role, args.model))

    try:
        if not probe.blocked(prompt):
            print("\nnot reproduced: the full prompt passes as %s." % args.role
                  + ("\ntry --role developer / --role user" if args.role == "system" else ""))
            return 1

        paragraphs = split_paragraphs(prompt)
        index = first_blocking_prefix(paragraphs, probe.blocked)
        result = {"role": args.role, "model": args.model, "chars": len(prompt),
                  "paragraphs": len(paragraphs), "first_blocking_prefix": index,
                  "calls": probe.calls, "windows": [], "sentences": []}
        if not index:
            print("\nreproduced only as a whole: no blocking prefix (accumulation "
                  "spans every paragraph).")
            return 1

        blocking_para = paragraphs[index - 1]
        alone = probe.blocked(blocking_para)
        result["blocking_paragraph"] = blocking_para
        result["paragraph_alone"] = alone

        if not args.quiet and not args.json:
            print("\n--- paragraph #%d of %d ---\n%s\n" % (index, len(paragraphs), blocking_para))

        # 句子级：单句放行、连起来才拦，通常是「两句连续文本」型指纹
        for sentence in split_sentences(blocking_para):
            hit = probe.blocked(sentence)
            result["sentences"].append({"text": sentence, "blocked": hit})

        windows = shrink(blocking_para, probe.blocked)
        result["windows"] = windows
        result["calls"] = probe.calls
        result["elapsed_s"] = round(time.time() - started, 1)
    except RuntimeError as exc:
        print("probe failed: %s" % exc, file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0

    print("\n=== verdict ===")
    print("role           : %s" % args.role)
    print("blocking para  : #%d (alone: %s)" % (index, "BLOCKED" if alone else "ok"))
    if len(windows) == 1:
        print("minimal window : %d chars" % len(windows[0]))
        print()
        print(windows[0])
    else:
        print("minimal windows: %d" % len(windows))
        for w in windows[:3]:
            print("\n  [%d chars] %s" % (len(w), w))
    print("\ncalls: %d, elapsed: %.1fs" % (probe.calls, result["elapsed_s"]))
    print("\nnext: change one word inside the window (keep the meaning), then")
    print("      python scripts/diagnose_11_128.py --check \"<rewritten text>\"")
    print("      a rewrite that returns PASSES can go into wb_proxy's sanitizer.")
    if len(windows) == 1:
        with open(os.path.join(tempfile.gettempdir(), "wb-11-128-window.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write(windows[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
