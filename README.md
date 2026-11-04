# WorkBuddy2API-Hub — 国际版、国内版多账号网关中枢

> [!IMPORTANT]
> **项目进入低频维护（2026-10-23） / Low-frequency maintenance**
>
> 大幅降低更新频率与 Issue / PR 处理速度。请先阅读风险说明，再决定是否继续使用。
>
> Updates and responses to issues / pull requests will be significantly reduced. Read the risk notice below before continuing.

> [!WARNING]
> **WorkBuddy 上游正在收紧对非官方客户端的识别与拦截。**
>
> - **封禁**：2026-10-23 下午起，非官方客户端的识别与拦截明显收紧。
> - **维护者**：近期工作压力增大，无法保证及时更新与响应。
> - **可用性**：上游可能随时进一步收紧，导致本项目不可用。
> - **账号风险**：使用非官方客户端造成的风控、限流或封禁，由使用者自行承担。
>
> **Upstream enforcement** tightened detection and blocking of unofficial clients from the afternoon of 2026-10-23. The maintainer is under increased workload and cannot guarantee timely updates or replies. The upstream may tighten further at any time; rate limits, account restrictions or bans caused by using an unofficial client are the user's responsibility.

本项目仅用于协议学习、研究与个人自用。请优先使用官方客户端，不要使用主账号，不要共享账号，也不要用于商业转售。

This project is for protocol research and personal use only. Prefer the official client, do not use your primary account, and do not resell or share access.

<p align="center">
  <a href="https://github.com/ardeyouxipianyi/workbuddy2api-hub/releases"><img src="https://img.shields.io/badge/Release-v1.10.9-2496ED?style=flat-square" alt="Version 1.10.9"></a>
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/API-OpenAI_Compatible-412991?style=flat-square" alt="OpenAI API">
  <img src="https://img.shields.io/badge/Dual_Realm-Intl_&_CN-0DBD8B?style=flat-square" alt="Dual Realm">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Maintenance-Low--frequency-c96f3d?style=flat-square" alt="Low-frequency maintenance">
</p>

## 核心特性

- **标准 API 兼容**：将 WorkBuddy（国际版/国内版）与 CodeArts 封装为标准 OpenAI 格式（Chat Completions / Responses），无缝支持 Codex、Claude Code、NextChat 等各类客户端。
- **开箱即用与多端部署**：便携版免装环境（Windows 自带精简运行时），支持 Docker、NAS（群晖/飞牛）一键部署及 OpenWrt 路由器固件。
- **多账号池与出口隔离**：支持浏览器 OAuth 快速导入、每账号独立出口代理槽绑定、设备指纹隔离、自动故障转移与配额轮转。
- **自动化福利与签到**：内置国内版全套成长任务、加油站签到与猫猫旅行，支持国际版每日活跃会话与 CodeArts 自动签到。
- **可视化管理看板**：提供 Web 仪表盘，支持实时请求日志、Token/积分透视、多 API Key 权限分发（模型/账号白名单）与额度护栏。

> ⚡ **Vibe Coding 产物**：本项目为 100% Vibe Coding 协同产物——人类开发者提出架构与业务意图，AI 助手端到端完成逆向分析、链路调度、WAF 指纹脱敏与界面编写。

> 📌 **提交代码贡献前**：请先查看并**严格遵循**贡献手册 [`CONTRIBUTING.md`](CONTRIBUTING.md)——提交格式、测试门禁与端到端冒烟要求都在那里（AI / 智能体请特别注意其中的硬性规则节）。

---

## 💖 赞助商

> 想出现在这里？联系 [ardeyouxipianyi@gmail.com](mailto:ardeyouxipianyi@gmail.com)

<table>
<tr>
<td width="180" align="center" valign="middle">
  <a href="https://agentrouter.org/register?aff=unrV"><img src="https://raw.githubusercontent.com/88lin/picx-images-hosting/master/90C5FAD072EA247822CB88BB32512A41.webp" alt="Agent Router" width="150"></a>
</td>
<td valign="middle"><b><a href="https://agentrouter.org/register?aff=unrV">Agent Router</a></b>&nbsp;是免费公益大模型 API 平台，支持 Claude-opus-5.5、GPT-6 Astra、GPT-6.1 Sol、deepseek-v4-flash 等主流模型，国内直连。注册送 ＄175（每日签到得 ＄25，被邀得 ＄50），支持 GitHub / LinuxDo 登录。</td>
</tr>
</table>


---

## 一、快速启动

### 1. 本机运行

- **Windows**：双击 `start-wb-proxy.bat`（静默后台运行 + 独立日志窗口）；如需前台控制台窗口，双击 `start-wb-proxy-visible.bat`。
- **macOS / Linux**：双击 `start-wb-proxy.command` 或在终端执行 `./start-wb-proxy.sh [端口]`（默认 8788，需要 Python 3.9+）。
- **局域网共享模式**：运行 `start-wb-proxy-lan.bat`（Windows）或 `./start-wb-proxy-lan.sh`（macOS/Linux），首次启动将自动生成高强度 API Key 并在控制台打印。
- 启动后访问：
  - **Web 看板**：`http://127.0.0.1:8788/`（默认访问密码 `admin`，首次登录请在设置中修改）
  - **API 地址**：`http://127.0.0.1:8788/v1`

### 2. Docker 部署

预编译多架构镜像发布在 GHCR，无需本地构建：

**方式一：一键脚本（推荐）**

```bash
# 官方源（直连 GitHub 环境）：
curl -fsSL https://raw.githubusercontent.com/ardeyouxipianyi/workbuddy2api-hub/main/quick-deploy.sh | bash

# 国内网络 / NAS 加速：
curl -fsSL https://gh-proxy.com/https://raw.githubusercontent.com/ardeyouxipianyi/workbuddy2api-hub/main/quick-deploy.sh | sudo bash
```

> 公网部署或配合反向代理：在管道前指定 `WB_DEPLOY_MODE=public bash`，并搭配 Nginx / Caddy / Cloudflare Tunnel 配置 TLS。

**方式二：单文件 Docker Compose**

```yaml
services:
  wb-proxy:
    image: ghcr.io/ardeyouxipianyi/workbuddy2api-hub:latest
    container_name: wb-proxy
    restart: unless-stopped
    ports:
      - "8788:8788"
    environment:
      - HOST=0.0.0.0
      - PORT=8788
      - TZ=Asia/Shanghai
    volumes:
      - ./accounts:/app/accounts    # 账号凭据与配置（持久化）
      - ./usage:/app/usage          # 用量流水日志（持久化）
```

更新镜像：`docker compose pull && docker compose up -d`。

### 3. CodeArts 原生第三出口

网关内置进程内直连华为云 CodeArts，支持聊天 SSE 协议转换与自动签到，无需单独运行第三方桥接服务：
1. 打开看板 →「设置 → CodeArts 接入」，勾选「启用 CodeArts 出口」并保存；
2. 切换至看板顶部「CodeArts」视图，点击「+ 添加账号 (OAuth)」完成华为云授权；
3. 在「设置 → API Key」中新建 Key 并绑定出口为 `CodeArts`（或全局通用）即可调用。

---

## 二、账号接入与 API Key 权限

### 1. 账号添加与代理出口绑定
- 打开看板 `http://127.0.0.1:8788/`，点击「+ 添加账号 (OAuth)」，在浏览器中完成官方登录授权即可自动入库。
- **独立代理出口槽（Proxy Slot）**：在看板中可按需配置并命名 HTTP/SOCKS5 出口代理（支持账号密码认证），支持将账号与特定代理槽位绑定，账号身份请求与出站调用均自动走该代理。

### 2. 多 API Key 权限管理
- 「设置」页支持创建多个独立 API Key：
  - **出口绑定**：可固定走国际版、国内版或 CodeArts；
  - **模型限制**：支持通配符白名单（如 `deepseek*`, `gpt-6-astra`），违规请求本机直接返回 400；
  - **账号白名单**：可精确限定该 Key 仅允许调度的账号范围；
  - **用量透视**：数据看板按 Key 独立统计调用次数、Token 消耗、缓存命中与积分。

---

## 三、客户端接入配置

- **Base URL**：`http://127.0.0.1:8788/v1`（局域网为 `http://<局域网IP>:8788/v1`）
- **API Key**：看板「设置」中添加并绑定的 Key
- **模型名称**：调用 `/v1/models` 中列出的任意官方对齐模型 ID（如 `deepseek-v4.1-flash`, `gpt-6-astra`, `hy3`）

**Codex CLI / Responses API**

```bash
export OPENAI_BASE_URL="http://127.0.0.1:8788/v1"
export OPENAI_API_KEY="你在看板设置中添加并绑定的API_Key"
```

**Claude Code / Anthropic Messages（实验性）**

网关支持实验性 Messages 协议适配，因长会话缓存命中率差异，默认关闭：
```bash
# 网关端设置 WB_ENABLE_ANTHROPIC_MESSAGES=1 开启后生效：
export ANTHROPIC_BASE_URL="http://127.0.0.1:8788"
export ANTHROPIC_API_KEY="你在看板设置中添加并绑定的API_Key"
```

---

## 四、常用环境变量

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `PORT` | `8788` | 网关监听端口 |
| `API_KEY` | 自动生成 | 初始 API Key（看板配置多 Key 后优先由看板管理） |
| `WB_DEPLOY_MODE` | `lan` | 部署模式：`lan`（0.0.0.0）、`local`（127.0.0.1）、`public` |
| `WB_MAX_PAYLOAD_BYTES` | `16777216` | 单请求体上限（字节，默认 16MB，支持 1–256 MB） |
| `WB_DEEPSEEK_FLASH_FORCE_SG` | `0` | 国际版 deepseek-v4.1-flash 是否强制出站走新加坡付费通道 |
| `WB_ENABLE_ANTHROPIC_MESSAGES` | `0` | 是否开启实验性 Anthropic Messages 协议转换 |
| `WB_BACKGROUND_MODEL_TARGET` | 留空 | 后台模型别名改写目标（如 DSH 客户端自动映射） |
| `WB_CA_BUNDLE` | 留空 | 自签根证书路径（供抓包调试或中间代理使用） |
| `WB_CN_CHAT_UPSTREAM` | 官方默认 | 国内版出站代理地址 |
| `WB_IDENTITY_OS` | 宿主系统 | 仅 CLI 身份：覆盖 `x-stainless-os`（如 `Linux` / `Windows`） |
| `WB_IDENTITY_ARCH` | 宿主架构 | 仅 CLI 身份：覆盖 `x-stainless-arch`（如 `x64` / `arm64`） |
| `WB_IDENTITY_NODE_VERSION` | 官方默认 | 仅 CLI 身份：覆盖 `x-stainless-runtime-version` |

遇到上游 `400 / 11-128` 时，先按 [`docs/TROUBLESHOOTING-11-128.md`](docs/TROUBLESHOOTING-11-128.md) 收集同一请求的
身份、最小请求和提示词对照结果；不要先轮换账号。

---

## 五、主要 API 端点

| 接口 | 方法 | 端点 | 说明 |
|---|---|---|---|
| 聊天补全 | `POST` | `/v1/chat/completions` | 标准 OpenAI 聊天接口（支持流式 SSE 与思维链回填） |
| 交互式响应 | `POST` | `/v1/responses` | OpenAI Responses 协议接口（Codex 专用） |
| 模型目录 | `GET` | `/v1/models` | 获取当前出口对齐的官方可用模型列表 |
| 生图 | `POST` | `/v1/images/generations` | 文生图 / 图生图（需在设置中启用媒体模块） |
| 生视频 | `POST` | `/v1/videos` | 异步生视频任务提交（本地并发排队与空闲调度） |
| 视频状态 | `GET` | `/v1/videos/<id>` | 轮询视频生成进度与结果 |
| 产物下载 | `GET` | `/v1/videos/<id>/content` | 下载视频 MP4 产物直链 |
| 健康检查 | `GET` | `/health` | 网关运行状态、可用账号数与就绪模型分布 |

---

## 六、测试验证

```bash
python tests/run_all.py            # 全部套件
python tests/run_all.py realm      # 只跑名字里含 realm 的
```

- 267 个套件：203 个 Python + 64 个 JS；JS 需要 PATH 上有 `node`，缺失时会跳过并提示。
- `tests/_mobile_check.py` 是独立的 Playwright 手机/桌面布局检查器（需自行安装 Playwright），按需手动运行，不在上面的套件集里。
- CI（`.github/workflows/tests.yml`）跑同一条命令：Ubuntu 上 python 3.9 与 3.12（3.9 是本项目声称的最低版本），Windows 上 python 3.12；推送 `v*` tag 时额外断言 **tag == 源码版本**（`-ci` 演练 tag 豁免）。

---

## 七、版本更新记录 (Changelog)

### Unreleased

- **补上退出取证：进程消失不再是无头案**：网关以 `pythonw` 静默启动时 stdout/stderr 都是空设备，运行日志只在内存环里——进程一旦非正常消失，那圈日志连同退出原因一起没了，事后只能看到「面板连不上、重启就好」。现在 `install_exit_diagnostics()` 在 `__main__` 入口就装上三层钩子：`faulthandler` 管原生崩溃（段错误 / C 扩展 abort，Python 层钩子在那时根本不会执行）、`sys.excepthook` 与 `threading.excepthook` 管未捕获异常（把类型、消息和栈打进日志通道）、`atexit` 记下正常退出。`os._exit()` 三条都绕不过，所以面板「关闭服务」那条路单独先写一行 `shutdown: requested from the panel` 再退出——它此前完全无痕。同时建议开启设置里的「日志落库」（`log_db_enabled`），让日志在进程死后仍能从 `usage/logs.sqlite3` 读回。新增 `tests/_test_exit_diagnostics.py`（6 项：钩子确实装上、未捕获异常与线程异常都落到日志通道且为 ERROR 级、重复安装不抛、关闭服务日志必须在 `os._exit` 之前）。发布包运行时清单同步补齐 `traceback` 及其依赖（`linecache` / `tokenize` / `textwrap` / `contextlib` / `itertools` 等 19 项），否则崩溃那一刻才会抛 ImportError。 / Exit forensics so a vanished process is no longer a dead end: launched headless under `pythonw`, the gateway's stdout and stderr both point at the null device and its runtime log lives only in an in-memory ring - when the process disappears unexpectedly, that log and the reason go with it, leaving just "the panel will not connect, restart it". `install_exit_diagnostics()` now installs three hooks at the `__main__` entry: `faulthandler` for native crashes (segfaults, C-extension aborts, where the Python-level hooks never run at all), `sys.excepthook` and `threading.excepthook` for uncaught exceptions (type, message and traceback into the log channel), and `atexit` for an orderly exit. `os._exit()` bypasses all three, so the panel's "shut down the service" path logs `shutdown: requested from the panel` before exiting - it used to leave no trace whatsoever. Turning on the "log database" setting (`log_db_enabled`) is also recommended, so the log can be read back from `usage/logs.sqlite3` after the process dies. New `tests/_test_exit_diagnostics.py` (6 checks: the hooks really install, uncaught and thread exceptions reach the log channel at ERROR level, re-installing does not raise, and the shutdown log line precedes `os._exit`). The portable runtime manifest gains `traceback` and its dependencies (19 entries including `linecache` / `tokenize` / `textwrap` / `contextlib` / `itertools`), which would otherwise raise ImportError at the exact moment the process is crashing.

- **修复 Codex 0.165 起持续 11-128（首句换了个名词，规则整条空转）**：`codex exec` 无论换哪个模型都在第一轮被上游 400 挡回（`Illegal API invocation from an unapproved channel`）。用请求转储定位到阻塞点是 `/v1/responses` 转成 chat 后的 4 条消息里那条 17KB 的 system 消息；`scripts/diagnose_11_128.py --check` 二分出最小窗口就是它的第一句。根因：脱敏规则钉死的是 `You are a coding agent running in the Codex CLI, a terminal-based coding assistant.`（cli 与逗号紧挨），而 0.165 起官方把这一句改成了 `… in the Codex CLI tool, a terminal-based …`——规则匹配不上就整条空转，不带 tool 的旧写法也一并漏过。现在两种写法各有规则，都统一改成 `Codex CLI application`：只换一个名词，身份、工具清单与行为一个字都不动。真机回归：`codex exec "say hi in one word"` 通，带工具调用的多轮任务走满 19 个工具、14,147 tokens 通过；`tests/_test_sanitize_fingerprint.py` 新增 3 项断言（两种写法都被改写、幂等、嵌在完整 system prompt 中间仍生效、system 角色走 identity 分支）。 / Fixed the persistent 11-128 that Codex 0.165 hits on every first turn: `codex exec` was answered with a 400 (`Illegal API invocation from an unapproved channel`) no matter which model it asked for. A request dump pinned the blocker to the 17KB system message among the four messages of a `/v1/responses` request converted to chat, and `scripts/diagnose_11_128.py --check` bisected the minimal window down to its first line. The cause: the sanitizer rule matched `You are a coding agent running in the Codex CLI, a terminal-based coding assistant.` (with `cli` glued to the comma), but 0.165 changed that sentence to `… in the Codex CLI tool, a terminal-based …`, so the rule never fired - and the older spelling without "tool" was left uncovered too. Both spellings now have a rule and both become `Codex CLI application`: one noun swapped, with the identity, the tool list and the behaviour untouched. Verified on the real CLI: `codex exec "say hi in one word"` passes, and a tool-calling multi-turn task completes all 19 tools over 14,147 tokens. `tests/_test_sanitize_fingerprint.py` gains 3 assertions (both spellings rewritten, idempotent, still applied when embedded in a full system prompt, and honoured for the system role).
- **`/v1/models` 支持 Anthropic 形状：修 VS Code Claude agent「没有模型」**：同一台机器上 Codex agent 能看到 WB Proxy 的模型、Claude agent 却一个都不显示——差别在清单形状。Anthropic 的条目是 `{"type":"model","id","display_name","created_at"}`，顶层还有 `has_more` / `first_id` / `last_id`；网关原先只回 OpenAI 形状（条目 `object:"model"`、没有 `type`）。Claude agent 与 Anthropic SDK 的 `models.list()` 按 `type == "model"` 过滤，于是读到空列表。现在带 `anthropic-version` 头的请求按 Anthropic 形状回答（不带该头的仍回 OpenAI 形状，Codex 等客户端不受影响），并补上 `GET /v1/models/<id>`（Anthropic 的 `models.retrieve()`；未知 id 回 404）。实测：带该头返回 19 条、`type` / `display_name` / `created_at` 齐全，不带该头仍是 `object: "list"`。新增 `tests/_test_anthropic_models.py`（8 项）。 / `/v1/models` now also speaks the Anthropic shape, which fixes "no models" in VS Code's Claude agent: on the same machine the Codex agent lists WB Proxy models while the Claude agent shows none, because Anthropic entries are `{"type":"model","id","display_name","created_at"}` with `has_more` / `first_id` / `last_id` on top, whereas the gateway only returned the OpenAI shape (`object:"model"`, no `type`). The Claude agent and the Anthropic SDK's `models.list()` filter on `type == "model"`, so they saw an empty list. Requests carrying an `anthropic-version` header now get the Anthropic shape (openai-shape clients such as Codex are unaffected), and `GET /v1/models/<id>` was added for `models.retrieve()` (unknown ids answer 404). Measured: with the header 19 entries with `type` / `display_name` / `created_at`, without it the unchanged `object: "list"`. New `tests/_test_anthropic_models.py` (8 checks).
- **智能体配置：网关地址改成下拉框（选项即 base_url），客户端卡片可「查看配置」**：连接信息的网关地址从文本框改成 `<select>`，选项直接是地址本身（`http://127.0.0.1:8788/v1` 与 `http://<局域网IP>:8788/v1`，不加「本机 / 局域网」前缀；`/agents` 新增 `gateway.lan_base_urls`，仅在绑定 `0.0.0.0` 时列出；只监听回环时才给一句提示指向 `start-wb-proxy-lan.bat`），与 API Key、默认模型用同一套自绘下拉控件，三个控件实测同为 28px 高；之前存过的自定义地址（反向代理 / 别的端口）会保留成一条选项，不会因为换控件被悄悄改掉。客户端卡片新增「查看配置」：`POST /agents/preview` 复用 `plan()` 的渲染管线（与真正写入同源，只读、不落盘），逐文件显示路径、状态（将新建 / 将修改 / 与现有内容一致）与完整内容，可一键复制；内容含写入客户端的 Key，界面里给了提示。顺带修掉一处真实缺陷：面板已配置 Key 时，默认「全局 API Key」原先仍返回启动器 Key，而 `identify_key` 只认面板 Key，写进客户端后每个请求都是 401——现在改为取第一把启用的面板 Key（预览功能正好把这个问题摆到台面上）。新增 `tests/_test_agents_preview.py`（10 项）与 8 项前端断言。 / Agent setup's gateway URL is now a `<select>` whose options are the addresses themselves (`http://127.0.0.1:8788/v1` and `http://<LAN IP>:8788/v1`, with no "local / LAN" prefix; `/agents` gained `gateway.lan_base_urls`, listed only when bound to `0.0.0.0`, and a loopback-only bind prints a hint pointing at `start-wb-proxy-lan.bat`); it uses the same self-drawn dropdown as the API-key and model fields and all three measure 28px high. A previously stored custom URL (reverse proxy, another port) survives as an extra option instead of being silently replaced. Each client card gained a "View config" button: `POST /agents/preview` reuses the same `plan()` renderer as a real apply (read-only, nothing written) and shows every file's path, state (will create / will change / already matches) and full contents, with one-click copy and a warning that the key is in there. Also fixed a real defect the preview exposed: with panel keys configured, the default "global API key" used to hand out the launcher key, which `identify_key` rejects, so every client request came back 401 — it now picks the first enabled panel key. New `tests/_test_agents_preview.py` (10 checks) plus eight front-end assertions.
- **修复出口替身误改写「当前出口本来就有的模型」**：上一条放宽「无归属出口的模型走 `*` 替身」时，把「没有**独占**归属」当成了「没人提供」——`glm-5.3`、`hy3` 这些两个出口都提供的模型没有独占归属，于是也被改写成 `deepseek-v4.1-flash`，用户在下拉里选了模型、实际跑的还是 deepseek。现在判定改为「**当前出口的目录认不认识这个模型**」（`realm_served_models()`：静态快照 + 已落盘的远程目录，本地只读、60 秒缓存，与 `/v1/models` 同源）：认识就绝不改写；不认识再看独占归属与账号就绪检查。实测 `glm-5.3` / `deepseek-v4-pro` 按原名跑，`gpt-5.5` / `codex-auto-review` 仍走替身。新增 2 项断言（共享模型不改写 + 目录判定本身）。 / Fix the per-exit stand-in rewriting models the current exit already serves: the previous relaxation treated "no *exclusive* owner" as "nobody serves it", so shared models like `glm-5.3` and `hy3` were also rewritten to `deepseek-v4.1-flash` — the user picked a model and deepseek ran anyway. The check is now "does the current exit's catalogue know this model" (`realm_served_models()`: static snapshot plus the cached remote catalogue, local reads only, 60-second cache, same source as `/v1/models`): known models are never rewritten; unknown ones fall through to the exclusive-owner and readiness checks. Verified live: `glm-5.3` / `deepseek-v4-pro` run under their own ids, `gpt-5.5` / `codex-auto-review` still take the stand-in. Two assertions added (shared models untouched, and the catalogue check itself).
- **修复出口替身不接管「任何出口都没有的模型」**：Codex 的自动审核（Approve for me）会调用它自己的内部模型 `codex-auto-review`，而这个模型上游没有——原先 `realm_alias_for()` 先问「提供该模型的那个出口有没有可用账号」，对没有归属出口的模型等于问 `count_ready(realm="")`，任何账号都能满足，于是永远不改写，`/v1/responses` 每次都 400 `11102 model [codex-auto-review] service info not found`，写文件被自动审核直接拒掉。现在只有**确实归属某个出口**的模型才做这项就绪检查；没有归属出口的模型（`codex-auto-review`、拼错的、上游下线的）直接走 `*` 替身。实测改写后同形态请求（`/v1/responses` + 3 个工具 + stream）返回 200，日志有 `realm alias: codex-auto-review -> deepseek-v4.1-flash`。新增 3 项断言。 / Fix the per-exit stand-in refusing models no exit serves: Codex's auto review ("Approve for me") calls its internal `codex-auto-review` model, which the upstream does not have. `realm_alias_for()` used to ask "does the exit that serves this model have a usable account?", which for a model with no owning exit means `count_ready(realm="")` — any account satisfies it, so the rewrite never happened and every `/v1/responses` call died with `11102 model [codex-auto-review] service info not found`, leaving writes auto-rejected. The readiness check now applies only to models that genuinely belong to an exit; models nobody serves (`codex-auto-review`, typos, retired ids) take the `*` stand-in. After the fix the same request shape (`/v1/responses`, three tools, stream) returns 200 and logs `realm alias: codex-auto-review -> deepseek-v4.1-flash`. Three assertions added.
- **修复 Codex 0.165 起持续 11-128（首句换了个名词，规则整条空转）**：`codex exec` 无论换哪个模型都在第一轮被上游 400 挡回（`Illegal API invocation from an unapproved channel`）。用请求转储定位到阻塞点是 `/v1/responses` 转成 chat 后的 4 条消息里那条 17KB 的 system 消息；`scripts/diagnose_11_128.py --check` 二分出最小窗口就是它的第一句。根因：脱敏规则钉死的是 `You are a coding agent running in the Codex CLI, a terminal-based coding assistant.`（cli 与逗号紧挨），而 0.165 起官方把这一句改成了 `… in the Codex CLI tool, a terminal-based …`——规则匹配不上就整条空转，不带 tool 的旧写法也一并漏过。现在两种写法各有规则，都统一改成 `Codex CLI application`：只换一个名词，身份、工具清单与行为一个字都不动。真机回归：`codex exec "say hi in one word"` 通，带工具调用的多轮任务走满 19 个工具、14,147 tokens 通过；`tests/_test_sanitize_fingerprint.py` 新增 3 项断言（两种写法都被改写、幂等、嵌在完整 system prompt 中间仍生效、system 角色走 identity 分支）。 / Fixed the persistent 11-128 that Codex 0.165 hits on every first turn: `codex exec` was answered with a 400 (`Illegal API invocation from an unapproved channel`) no matter which model it asked for. A request dump pinned the blocker to the 17KB system message among the four messages of a `/v1/responses` request converted to chat, and `scripts/diagnose_11_128.py --check` bisected the minimal window down to its first line. The cause: the sanitizer rule matched `You are a coding agent running in the Codex CLI, a terminal-based coding assistant.` (with `cli` glued to the comma), but 0.165 changed that sentence to `… in the Codex CLI tool, a terminal-based …`, so the rule never fired - and the older spelling without "tool" was left uncovered too. Both spellings now have a rule and both become `Codex CLI application`: one noun swapped, with the identity, the tool list and the behaviour untouched. Verified on the real CLI: `codex exec "say hi in one word"` passes, and a tool-calling multi-turn task completes all 19 tools over 14,147 tokens. `tests/_test_sanitize_fingerprint.py` gains 3 assertions (both spellings rewritten, idempotent, still applied when embedded in a full system prompt, and honoured for the system role).
- **修复自绘下拉的展开层被父容器裁掉**：展开层原先挂在下拉框自己的 `.cs-wrap` 里、用 absolute 定位，只要祖先有 `overflow`（卡片、表格滚动区、`section{overflow:auto}`）就会被裁掉——「智能体配置」的连接信息卡片即一例：展开后只能在那 300px 宽的输入框里滚动，看不到整张列表。现在面板 portal 到 `<body>` 并用 `position:fixed` 按触发器 rect 定位：宽度对齐触发器（超出视口时夹取）、贴近底部时自动向上翻、滚动/缩放时重新定位而不关闭；关闭态仍用 opacity / pointer-events 隐藏，行点击与悬停事件改绑到面板自身，页面重渲染留下的孤儿面板在下次扫描时清理。原生 select 的 value / change / 表单提交与 aria 语义不变。自定义下拉套件新增 1 项断言（20 项）。 / Fix the self-drawn dropdown being clipped by its container: the panel used to live inside the field's own `.cs-wrap` with absolute positioning, so any ancestor with `overflow` (cards, table scroll areas, `section{overflow:auto}`) cut it off — the agent-config connection card is one: the open list could only scroll inside the ~300px input. The panel is now portaled to `<body>` with `position:fixed`, positioned from the trigger's rect (width matched to the trigger and clamped to the viewport, flips upward near the bottom edge, repositions instead of closing on scroll/resize); the closed state still hides it via opacity / pointer-events, row click and hover handlers moved onto the panel itself, and panels orphaned by a re-render are pruned on the next scan. Native select value / change / form submission and aria semantics are unchanged. One assertion added to the custom-select suite (20).
- **跨出口模型替身（`realm_model_aliases`，默认关闭）**：VS Code 的 Codex agent 只能从 Codex 自带目录里挑模型（`gpt-5.5` / `gpt-6-sol` 等），界面上没有地方填国内版模型名，而国内版出口一个 `gpt-*` 都不提供——于是它的每次请求都停在「模型只在国际版提供」的区域自检上，本地跑不起来。`accounts/settings.json` 新增 `realm_model_aliases`（`{"模型 id": "替身模型"}`，精确 id 优先、`*` 兜底）：请求的模型只由另一个出口提供、**且那个出口当前没有可用账号**时，把它换成当前出口能提供的替身，三条生成入口（`/v1/responses`、`/v1/messages`、`/v1/chat/completions`）都在构造上游请求体之前改写。替身自身必须是当前出口能提供的模型（否则不作数）；对面出口一旦有可用账号就完全不介入，仍按原样报错并提示换 Key 出口——避免把「配错了」变成静默降级。改写会落一行 `realm alias: <原模型> -> <替身> (exit <realm>)` 日志，响应与用量记录的是**实际执行**的模型。空表 = 关闭（老安装行为不变）。新增 10 项断言。 / Per-exit model stand-ins (`realm_model_aliases`, off by default): VS Code's Codex agent can only pick from Codex's own catalogue (`gpt-5.5`, `gpt-6-sol`, ...) and has nowhere to type a China-only model id, while the China exit serves no `gpt-*` at all — so every one of its requests died on the realm self-check. A new `realm_model_aliases` map in `accounts/settings.json` (`{"model id": "stand-in"}`, exact id first, then `*`) rewrites such a request onto a model the current exit serves, but only when the exit that owns the model has no usable account right now; all three generation routes (`/v1/responses`, `/v1/messages`, `/v1/chat/completions`) apply it before the upstream body is built. The stand-in must itself be servable by that exit, and the map never engages while the owning exit has an account — that case keeps the explicit "use a key bound to that exit" error instead of a silent downgrade. Each rewrite logs `realm alias: <requested> -> <stand-in> (exit <realm>)`, and both the response and the usage row name the model that actually ran. An empty map disables the feature, so existing installs are unchanged. Ten assertions added.

完整历史版本与详细变更日志请查阅 **[docs/CHANGELOG.md](docs/CHANGELOG.md)**。

---

## 八、致谢与引用声明 (Credits & References)

在协议逆向、风控规避、任务链路与工程化设计过程中，本项目参考、吸纳并致谢以下优秀开源项目与技术成果（排名不分先后）：

### 核心逆向与协议参考
- **[Sliverkiss/workbuddy2api](https://github.com/Sliverkiss/workbuddy2api)**：成长任务逆向、设备指纹派生（`derive_id`）、调度器（`Scheduler`）与 `reasoning_content` 回填设计；
- **[L0NE-6/WorkBuddy-Daily](https://github.com/L0NE-6/WorkBuddy-Daily)**：国内版微信小程序专属事件指纹与动态专家深链任务模型；
- **[88lin/workbuddy-auto-signin](https://github.com/88lin/workbuddy-auto-signin)**：猫猫日常旅行与成长能量开盲盒（Buddy 盲盒）安全生命周期；
- **[linguo2625469/workbuddy2api-panel](https://github.com/linguo2625469/workbuddy2api-panel)**：国内版连登管家闭环逻辑与轻量对话活跃上报事件；
- **[Zhengyuuuui/workbuddy2api](https://github.com/Zhengyuuuui/workbuddy2api)**：国际版 11140 风控限制识别、冷却规避与故障排查清单；
- **[yuanyuanyuan430/workbuddy2api-hub](https://github.com/yuanyuanyuan430/workbuddy2api-hub)**：国际版 EdgeOne CDN 证书错配排查与活跃上报优雅降级方案；
- **[CangShui/workbuddy-cliproxy-fix](https://github.com/CangShui/workbuddy-cliproxy-fix)** & **[lovingfish/workbuddy-cliproxy](https://github.com/lovingfish/workbuddy-cliproxy)**：早期客户端代理修复与网关通信原型；
- **[mmqz/cpa-multi-plugins](https://github.com/mmqz/cpa-multi-plugins)**：多插件管理与出站调度结构参考；
- **[ardeyouxipianyi/workbuddy2api](https://github.com/ardeyouxipianyi/workbuddy2api)**：国内版早期分发包逆向分析与出站 User-Agent 规范；

### 工程化与生态基础
- **[aodianjun/workbuddy2api-hub](https://github.com/aodianjun/workbuddy2api-hub)**：OpenWrt 路由器打包配方（`.ipk` / `.apk`）与系统服务支持；
- **[astral-sh/python-build-standalone](https://github.com/astral-sh/python-build-standalone)**：Windows 便携版免安装精简独立 Python 运行时构建基石；
- **[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)**：DSH 客户端协议与提示词指纹清洗规避参考。

感谢所有向本项目提交 PR、反馈 Issue 与分享实测样本的社区贡献者！

---

## 九、免责声明 (Disclaimer)

本项目仅用于协议学习与个人开发测试，不提供任何商业服务或可用性担保。因使用非官方客户端产生的账号风控、限制或封禁由使用者自行承担，请优先使用官方客户端。
