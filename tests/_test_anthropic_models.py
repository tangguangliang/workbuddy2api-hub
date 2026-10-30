#!/usr/bin/env python3
"""`/v1/models` 的两种形状：OpenAI（默认）与 Anthropic（带 anthropic-version）。

回归背景：VS Code 的 Claude agent 与 Anthropic SDK 的 `models.list()` 按
`type == "model"` 过滤条目，并期望顶层有 `has_more` / `first_id` / `last_id`。
网关只回 OpenAI 形状（条目是 `object: "model"`、没有 `type`）时，这些客户端读到
的是空列表——界面上就是「没有模型」；同一台机器上的 Codex agent 读 `object`，
所以 Codex 有模型、Claude 没有。
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import wb_proxy as P  # noqa: E402

OPENAI_ENTRY = {
    "id": "deepseek-v4.1-flash",
    "object": "model",
    "created": 1793333363,
    "owned_by": "workbuddy",
    "name": "Deepseek-V4.1-Flash",
}


class AnthropicModelsPayloadTests(unittest.TestCase):
    def test_entry_shape(self):
        payload = P.anthropic_models_payload([OPENAI_ENTRY])
        self.assertEqual(len(payload["data"]), 1)
        item = payload["data"][0]
        self.assertEqual(item["type"], "model")
        self.assertEqual(item["id"], "deepseek-v4.1-flash")
        self.assertEqual(item["display_name"], "Deepseek-V4.1-Flash")
        self.assertIn("created_at", item)
        self.assertNotIn("object", item)

    def test_top_level_has_anthropic_pagination_fields(self):
        payload = P.anthropic_models_payload(
            [OPENAI_ENTRY, dict(OPENAI_ENTRY, id="glm-5.3", name="GLM-5.3")])
        self.assertIs(payload["has_more"], False)
        self.assertEqual(payload["first_id"], "deepseek-v4.1-flash")
        self.assertEqual(payload["last_id"], "glm-5.3")
        self.assertEqual([m["id"] for m in payload["data"]],
                         ["deepseek-v4.1-flash", "glm-5.3"])

    def test_display_name_falls_back_to_id(self):
        payload = P.anthropic_models_payload([{"id": "hy3"}])
        self.assertEqual(payload["data"][0]["display_name"], "hy3")

    def test_entries_without_id_are_skipped(self):
        payload = P.anthropic_models_payload([{}, {"id": ""}, OPENAI_ENTRY, None])
        self.assertEqual([m["id"] for m in payload["data"]], ["deepseek-v4.1-flash"])

    def test_empty_list_has_no_anchor_ids(self):
        payload = P.anthropic_models_payload([])
        self.assertEqual(payload["data"], [])
        self.assertNotIn("first_id", payload)
        self.assertNotIn("last_id", payload)

    def test_openai_shape_untouched(self):
        # 同一个 helper 不能把 OpenAI 那条路改坏：model_entry 仍然给 object。
        entry = P.model_entry("deepseek-v4.1-flash", {})
        self.assertEqual(entry["object"], "model")
        self.assertNotIn("type", entry)


class ModelsRouteWiringTests(unittest.TestCase):
    """源码级契约：两条形状的分支真的接在路由上（漏接时单测全绿、线上照旧）。

    与 _test_dashboard_handlers.js 同一个思路：文本断言能覆盖「分支被删掉但
    helper 还在」这种静默退化。
    """

    def setUp(self):
        with open(os.path.join(ROOT, "wb_proxy.py"), encoding="utf-8") as fh:
            self.source = fh.read()

    def test_list_route_switches_on_anthropic_version(self):
        # 判定是模块级函数：单测里用 `object.__new__(Handler)` 或只有 .headers 的
        # 假对象调路由，方法形式在那种场景就是 AttributeError。
        self.assertIn("def wants_anthropic_shape(headers)", self.source)
        self.assertIn('headers.get("anthropic-version")', self.source)
        self.assertIn('wants_anthropic_shape(getattr(self, "headers", None))',
                      self.source)

    def test_single_model_route_exists(self):
        self.assertIn("def _get_v1_model(self, model_id)", self.source)
        self.assertIn('path.startswith("/v1/models/")', self.source)


if __name__ == "__main__":
    unittest.main()
