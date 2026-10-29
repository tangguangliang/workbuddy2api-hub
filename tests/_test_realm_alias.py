#!/usr/bin/env python3
"""出口替身模型（realm_model_aliases）的行为用例。

背景：VS Code 的 Codex agent 只能从 Codex 自己的模型目录（gpt-5.5 / gpt-6-sol
等）里挑，而国内版出口一个都不提供，界面上也没有地方填国内版模型名。网关加了
一层「出口替身」：只有在「请求的模型这个出口不提供」且「提供它的那个出口当前
没有可用账号」时，才把模型换成配置里的替身。

这几条断言钉住三件事：
  1. 精确 id 优先于 `*`；
  2. 替身本身必须能被当前出口提供，否则不改写（换一个同样不可用的模型没有意义）；
  3. 对面出口有可用账号时绝不改写 —— 那种场景正确答案是换 Key 出口 / 切面板，
     静默降级会把「配错了」变成「跑得慢、账对不上」。
"""
import os
import sys
import tempfile
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import wb_proxy as P  # noqa: E402
import wb_settings  # noqa: E402


class FakePool(object):
    """Just enough of AccountPool for the readiness guard."""

    def __init__(self, ready):
        self.ready = ready
        self.asked = []

    def count_ready(self, realm=None, model=None, allowed=None):
        self.asked.append(realm)
        return self.ready


class RealmAliasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wb-alias-")
        self.accounts = os.path.join(self.tmp, "accounts")
        os.makedirs(self.accounts, exist_ok=True)
        self._old_dir = P.ACCOUNTS_DIR
        self._old_pool = P.POOL
        P.ACCOUNTS_DIR = self.accounts
        P.POOL = FakePool(0)

    def tearDown(self):
        P.ACCOUNTS_DIR = self._old_dir
        P.POOL = self._old_pool
        for base, _dirs, files in os.walk(self.tmp, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(base, name))
                except OSError:
                    pass
            try:
                os.rmdir(base)
            except OSError:
                pass

    def alias(self, mapping):
        wb_settings.set_realm_model_aliases(self.accounts, mapping)

    # -- no configuration means no rewriting -------------------------------
    def test_without_aliases_nothing_is_rewritten(self):
        self.assertEqual(P.realm_alias_for("gpt-5.5", "cn"), "")

    def test_same_realm_model_is_left_alone(self):
        self.alias({"*": "deepseek-v4.1-flash"})
        self.assertEqual(P.realm_alias_for("deepseek-v4.1-flash", "cn"), "")

    # -- the map itself ----------------------------------------------------
    def test_wildcard_covers_every_codex_catalogue_model(self):
        self.alias({"*": "deepseek-v4.1-flash"})
        for model in ("gpt-5.5", "gpt-6-sol", "gpt-6-astra", "gpt-5.6-terra"):
            self.assertEqual(P.realm_alias_for(model, "cn"), "deepseek-v4.1-flash",
                             model)

    def test_exact_id_wins_over_the_wildcard(self):
        self.alias({"*": "deepseek-v4.1-flash", "gpt-5.5": "glm-5.3"})
        self.assertEqual(P.realm_alias_for("gpt-5.5", "cn"), "glm-5.3")
        self.assertEqual(P.realm_alias_for("gpt-6-sol", "cn"), "deepseek-v4.1-flash")

    def test_stand_in_that_the_exit_cannot_serve_is_refused(self):
        # gpt-6-sol 也是国际版独占：用它当替身只会把 400 换个说法。
        self.alias({"*": "gpt-6-sol"})
        self.assertEqual(P.realm_alias_for("gpt-5.5", "cn"), "")

    # -- the readiness guard ----------------------------------------------
    def test_no_rewrite_when_the_owning_exit_has_an_account(self):
        self.alias({"*": "deepseek-v4.1-flash"})
        P.POOL = FakePool(1)
        self.assertEqual(P.realm_alias_for("gpt-5.5", "cn"), "")
        # 检查的是「提供该模型的那个出口」，不是当前出口。
        self.assertEqual(P.POOL.asked, ["intl"])

    def test_rewrite_when_the_owning_exit_has_no_account(self):
        self.alias({"*": "deepseek-v4.1-flash"})
        P.POOL = FakePool(0)
        self.assertEqual(P.realm_alias_for("gpt-5.5", "cn"), "deepseek-v4.1-flash")

    def test_model_no_exit_serves_is_aliased_even_with_accounts(self):
        # Codex 的内部模型 codex-auto-review（以及拼错的、上游下线的模型名）没有
        # 任何出口提供它，所以「拥有它的出口有没有账号」并不适用：不改写就一定是
        # 上游 11102 service info not found。这里曾经用 count_ready(realm="")
        # 判断，任何账号都能满足它，于是 Codex 的自动审核调用永远拿不到替身、
        # 每次都 400，写文件被自动审核直接拒掉。
        self.alias({"*": "deepseek-v4.1-flash"})
        P.POOL = FakePool(2)
        self.assertEqual(P.realm_alias_for("codex-auto-review", "cn"),
                         "deepseek-v4.1-flash")
        self.assertEqual(P.realm_alias_for("definitely-not-a-model", "cn"),
                         "deepseek-v4.1-flash")

    def test_unknown_model_without_a_map_entry_is_untouched(self):
        self.alias({"gpt-5.5": "deepseek-v4.1-flash"})
        P.POOL = FakePool(0)
        self.assertEqual(P.realm_alias_for("codex-auto-review", "cn"), "")

    def test_shared_models_of_this_exit_are_never_rewritten(self):
        # 回归：曾把「没有独占归属」当成「没人提供」，于是 glm-5.3 / hy3 这些
        # 两个出口都有的模型也被 `*` 改写成 deepseek-v4.1-flash —— 用户在下拉里
        # 选了 glm-5.3，实际跑的却是 deepseek。
        # 只挑内置快照里就有的模型：space-bunny 这类只出现在远程目录的模型
        # 在测试里没有缓存可读，交给线上路径去保证。
        self.alias({"*": "deepseek-v4.1-flash"})
        P.POOL = FakePool(2)
        for model in ("glm-5.3", "hy3", "deepseek-v4.1-flash"):
            self.assertEqual(P.realm_alias_for(model, "cn"), "", model)

    def test_catalog_knows_which_exit_serves_what(self):
        cn = P.realm_served_models("cn")
        intl = P.realm_served_models("intl")
        self.assertIn("glm-5.3", cn)
        self.assertIn("deepseek-v4.1-flash", cn)
        self.assertNotIn("gpt-5.5", cn)
        self.assertIn("gpt-5.5", intl)

    # -- what the handler does with it -------------------------------------
    def test_handler_rewrites_every_body_it_is_given(self):
        self.alias({"*": "deepseek-v4.1-flash"})
        outer = {"model": "gpt-5.5", "stream": True}
        inner = {"model": "gpt-5.5", "messages": []}
        got = P.Handler._apply_realm_model_alias(types.SimpleNamespace(), "cn",
                                                 outer, inner)
        self.assertEqual(got, "deepseek-v4.1-flash")
        self.assertEqual(outer["model"], "deepseek-v4.1-flash")
        self.assertEqual(inner["model"], "deepseek-v4.1-flash")
        self.assertEqual(outer["stream"], True)          # untouched fields stay
        self.assertEqual(inner["messages"], [])

    def test_handler_leaves_the_body_alone_without_a_match(self):
        outer = {"model": "gpt-5.5"}
        got = P.Handler._apply_realm_model_alias(types.SimpleNamespace(), "cn", outer)
        self.assertEqual(got, "")
        self.assertEqual(outer["model"], "gpt-5.5")

    # -- settings hygiene ---------------------------------------------------
    def test_bad_map_entries_are_dropped_and_empty_map_is_removed(self):
        stored = wb_settings.set_realm_model_aliases(
            self.accounts, {"gpt-5.5": "glm-5.3", " ": "x", "y": 3})
        self.assertEqual(stored, {"gpt-5.5": "glm-5.3"})
        wb_settings.set_realm_model_aliases(self.accounts, {})
        self.assertEqual(wb_settings.realm_model_aliases(self.accounts), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
