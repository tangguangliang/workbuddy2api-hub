#!/usr/bin/env python3
"""`wb_agents.preview()` 与局域网地址探测（对应面板「查看配置」「网关地址提示」）。

面板新增两件事：连接信息里列出本机 / 局域网的网关地址，客户端卡片上能「查看配置」。
后者靠 `/agents/preview`，它必须是**只读**的、而且渲染出来的字节要和真正
`integrate()` 写下去的完全一致——否则用户按预览抄到别的机器上会得到另一份配置。

这几条断言钉住：不落盘、与 integrate 同源、重复预览会变成 changed=False、
未知客户端报 AgentConfigError，以及地址探测不返回回环 / 链路本地地址。
"""
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import wb_agents as A  # noqa: E402
import wb_proxy as P  # noqa: E402

BASE = "http://127.0.0.1:8788/v1"
KEY = "sk-preview-test"


class LanAddressTests(unittest.TestCase):
    def test_never_returns_loopback_or_link_local(self):
        for addr in P.lan_ipv4_addresses():
            self.assertTrue(isinstance(addr, str) and addr, addr)
            self.assertFalse(addr.startswith("127."), addr)
            self.assertFalse(addr.startswith("169.254."), addr)

    def test_result_is_deduplicated(self):
        addrs = P.lan_ipv4_addresses()
        self.assertEqual(len(addrs), len(set(addrs)))


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="wb-preview-")
        self.accounts = tempfile.mkdtemp(prefix="wb-preview-acc-")

    def tearDown(self):
        for path in (self.home, self.accounts):
            shutil.rmtree(path, ignore_errors=True)

    def test_preview_renders_files_without_writing_anything(self):
        result = A.preview("claude-code", BASE, KEY, model="deepseek-v4.1-flash",
                           home=self.home)
        self.assertEqual(result["client"], "claude-code")
        self.assertTrue(result["files"], "preview must render at least one file")
        for entry in result["files"]:
            self.assertIn("content", entry)
            self.assertIn("path", entry)
            self.assertTrue(entry["changed"], "a fresh home cannot already match")
            self.assertFalse(entry["existed"], entry["path"])

    def test_preview_is_byte_identical_to_what_integrate_writes(self):
        preview = A.preview("claude-code", BASE, KEY, model="deepseek-v4.1-flash",
                            home=self.home)
        applied = A.integrate(self.accounts, "claude-code", BASE, KEY,
                              model="deepseek-v4.1-flash", home=self.home)
        written = {entry["path"]: entry for entry in applied["files"]}
        self.assertEqual(set(written), {entry["path"] for entry in preview["files"]})
        for entry in preview["files"]:
            with open(entry["path"], encoding="utf-8") as fh:
                on_disk = fh.read()
            self.assertEqual(on_disk, entry["content"], entry["path"])

    def test_second_preview_reports_unchanged(self):
        A.integrate(self.accounts, "claude-code", BASE, KEY,
                    model="deepseek-v4.1-flash", home=self.home)
        again = A.preview("claude-code", BASE, KEY, model="deepseek-v4.1-flash",
                          home=self.home)
        self.assertTrue(again["files"])
        for entry in again["files"]:
            self.assertFalse(entry["changed"], entry["path"])

    def test_unknown_client_is_a_config_error(self):
        with self.assertRaises(A.AgentConfigError):
            A.preview("no-such-client", BASE, KEY, home=self.home)


class KeyResolutionTests(unittest.TestCase):
    """一键配置写进客户端的 Key 必须是网关真正接受的那把。

    回归：面板里配过 Key 之后，identify_key 只认面板 Key；而「全局 API Key」
    这条默认路径原先返回静态/启动器 API_KEY，写进客户端后每个请求都是 401。
    预览功能把这个矛盾摆到台面上（预览里能直接看到那把 Key），一起钉住。
    """

    def setUp(self):
        self._old_api_key = P.API_KEY
        self._old_keys = P.configured_keys
        P.API_KEY = "wb-launcher-key"

    def tearDown(self):
        P.API_KEY = self._old_api_key
        P.configured_keys = self._old_keys

    def _resolve(self, payload, keys):
        P.configured_keys = lambda: keys
        return P.Handler._agents_resolve_key(None, payload, [])

    def test_panel_key_wins_over_the_launcher_key(self):
        keys = [{"id": "k1", "name": "local", "key": "panel-key-1", "enabled": True}]
        self.assertEqual(self._resolve({}, keys), "panel-key-1")
        self.assertEqual(self._resolve({"key_id": "__global"}, keys), "panel-key-1")

    def test_disabled_panel_keys_are_skipped(self):
        keys = [
            {"id": "k1", "name": "off", "key": "disabled-key", "enabled": False},
            {"id": "k2", "name": "on", "key": "panel-key-2", "enabled": True},
        ]
        self.assertEqual(self._resolve({}, keys), "panel-key-2")

    def test_launcher_key_is_still_used_without_panel_keys(self):
        self.assertEqual(self._resolve({}, []), "wb-launcher-key")
        self.assertEqual(self._resolve({"key_id": "__global"}, []), "wb-launcher-key")

    def test_explicit_key_id_is_honoured(self):
        keys = [
            {"id": "k1", "name": "local", "key": "panel-key-1", "enabled": True},
            {"id": "k2", "name": "ds", "key": "panel-key-2", "enabled": True},
        ]
        self.assertEqual(self._resolve({"key_id": "k2"}, keys), "panel-key-2")
        with self.assertRaises(A.AgentConfigError):
            self._resolve({"key_id": "nope"}, keys)


if __name__ == "__main__":
    unittest.main()
