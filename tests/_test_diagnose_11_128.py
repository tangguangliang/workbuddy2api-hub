#!/usr/bin/env python3
"""`scripts/diagnose_11_128.py` 的纯函数用例（不联网、不碰真实账号）。

工具本身要打真实上游才能定位指纹，那部分没法进 CI；能钉住的是它**怎么决定下一
枪打哪里**：段落切分、前缀扫描、二分收缩的边界条件，以及探针预算。这些逻辑错
了不会报错，只会把结论指向一段无关文本——比崩溃更难发现，所以单独覆盖。
"""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "diagnose_11_128", os.path.join(ROOT, "scripts", "diagnose_11_128.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)


class SplitTests(unittest.TestCase):
    def test_paragraphs_split_on_blank_lines(self):
        # 段落保持原样（只丢弃空段）：块内缩进与行尾空白是原文的一部分，
        # 交给探针时不能被悄悄改掉，否则二分定位到的就不是客户端真正发的内容。
        self.assertEqual(D.split_paragraphs("a\n\nb\n\n\n c \n"), ["a", "b", " c \n"])
        self.assertEqual(D.split_paragraphs("single"), ["single"])
        self.assertEqual(D.split_paragraphs("   "), [])

    def test_sentences_keep_trailing_punctuation(self):
        self.assertEqual(D.split_sentences("One. Two! Three?  Four"),
                         ["One.", "Two!", "Three?", "Four"])

    def test_head_collapses_whitespace_and_ellipsis(self):
        self.assertEqual(D._head("a\n  b   c"), "a b c")
        self.assertTrue(D._head("x" * 100, limit=10).endswith("\u2026"))


class PrefixScanTests(unittest.TestCase):
    def test_finds_first_blocking_prefix(self):
        paras = ["p1", "p2", "p3"]
        seen = []

        def blocked(text):
            seen.append(text)
            return text.count("\n\n") >= 1        # 两段连起来才拦

        self.assertEqual(D.first_blocking_prefix(paras, blocked), 2)
        self.assertEqual(seen, ["p1", "p1\n\np2"])

    def test_zero_when_nothing_blocks(self):
        self.assertEqual(D.first_blocking_prefix(["a", "b"], lambda t: False), 0)


class ShrinkTests(unittest.TestCase):
    def test_finds_the_span_where_both_halves_pass(self):
        text = "aaaa bbbb TRIGGER cccc dddd"

        def blocked(candidate):
            return "TRIGGER" in candidate

        windows = D.shrink(text, blocked)
        self.assertTrue(windows, "shrink must return at least one window")
        for window in windows:
            self.assertIn("TRIGGER", window)
            left, right = D._halves(window)
            self.assertFalse(blocked(left), "left half of a minimal window must pass")
            self.assertFalse(blocked(right), "right half of a minimal window must pass")

    def test_halves_never_return_empty_side(self):
        left, right = D._halves("short text")
        self.assertTrue(left.strip())
        self.assertTrue(right.strip())


class ProbeBudgetTests(unittest.TestCase):
    def test_budget_is_enforced_before_the_request(self):
        probe = D.Probe("http://127.0.0.1:1", "k", max_calls=1, quiet=True)
        probe.calls = 1
        with self.assertRaises(RuntimeError):
            probe.blocked("anything")

    def test_explicit_key_wins(self):
        self.assertEqual(D.api_key("explicit-key"), "explicit-key")


if __name__ == "__main__":
    unittest.main()
