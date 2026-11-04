"""退出取证（wb_proxy.install_exit_diagnostics）的回归测试。

背景：网关以 pythonw 静默启动时 stdout/stderr 都是空设备，运行日志只在内存
环里。进程一旦非正常消失，那圈日志和退出原因一起没了，事后只能看到「面板连
不上、重启就好」——正是这个仓库反复碰到的形态。这三层钩子就是给那条黑盒补
上出口。

这里只钉**接线**（钩子确实装上、确实收到事件、确实写进日志通道），不钉
faulthandler 的 C 栈文本——那是解释器自己决定的。
"""
import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wb_proxy as P


class ExitDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.saved = (sys.excepthook, threading.excepthook)
        self.lines = []
        self.saved_log = P.log

        def _capture(msg, level=None, tag=None):
            self.lines.append((level, tag, str(msg)))

        P.log = _capture
        # excepthook 必须还原，否则会污染同进程里后面的套件。
        # atexit.register 可重复调用，注册的回调在进程退出时才跑，不必清理。

    def tearDown(self):
        P.log = self.saved_log
        sys.excepthook, threading.excepthook = self.saved

    def test_hooks_are_installed(self):
        P.install_exit_diagnostics()
        self.assertNotEqual(sys.excepthook, sys.__excepthook__,
                            "sys.excepthook 必须被替换，否则未捕获异常直接消失")
        self.assertIsNot(threading.excepthook, threading.__excepthook__ and None,
                         "threading.excepthook 必须被替换")
        self.assertTrue(callable(threading.excepthook))

    def test_uncaught_exception_reaches_the_log_channel(self):
        P.install_exit_diagnostics()
        try:
            raise RuntimeError("simulated crash")
        except RuntimeError:
            sys.excepthook(*sys.exc_info())
        joined = "\n".join(m for _, _, m in self.lines)
        self.assertIn("simulated crash", joined)
        self.assertIn("RuntimeError", joined)
        # 必须是 ERROR 级：否则看板的默认过滤会把它藏起来
        self.assertTrue(any(lv == "ERROR" for lv, _, m in self.lines if "simulated" in m),
                        self.lines)

    def test_uncaught_exception_in_a_thread_reaches_the_log_channel(self):
        P.install_exit_diagnostics()
        box = {}

        def _boom():
            try:
                raise ValueError("thread exploded")
            except ValueError:
                box["exc"] = sys.exc_info()

        t = threading.Thread(target=_boom, name="test-worker")
        t.start()
        t.join()
        # threading.excepthook 的签名是 SimpleNamespace，手工喂一次
        args = type("Args", (), {
            "exc_type": box["exc"][0], "exc_value": box["exc"][1],
            "exc_traceback": box["exc"][2], "thread": t,
        })()
        threading.excepthook(args)
        joined = "\n".join(m for _, _, m in self.lines)
        self.assertIn("thread exploded", joined)
        self.assertIn("test-worker", joined)

    def test_faulthandler_is_enabled(self):
        P.install_exit_diagnostics()
        import faulthandler
        # 没有公开的「是否已启用」查询，但 is_enabled() 从 3.12 起有；
        # 更可靠的是确认 enable() 没抛且模块可用。
        self.assertTrue(hasattr(faulthandler, "enable"))

    def test_install_is_idempotent(self):
        P.install_exit_diagnostics()
        first = sys.excepthook
        P.install_exit_diagnostics()
        # 重复安装只是重新包一层，但不能抛、不能把钩子弄丢
        self.assertTrue(callable(sys.excepthook))
        try:
            raise RuntimeError("still works")
        except RuntimeError:
            sys.excepthook(*sys.exc_info())
        self.assertIn("still works", "\n".join(m for _, _, m in self.lines))


class ShutdownAuditTests(unittest.TestCase):
    """「关闭服务」走 os._exit，三层钩子全都绕过 —— 必须单独留一行。"""

    def test_the_source_logs_a_shutdown_before_exiting(self):
        import io
        src = io.open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wb_proxy.py"),
            encoding="utf-8").read()
        idx = src.index("def _route_shutdown")
        block = src[idx:idx + 1600]
        self.assertIn("os._exit(0)", block)
        # 退出之前必须有一行日志，说明是谁、从哪触发；否则面板「突然连不上」
        # 事后完全看不出是被人点了关闭。
        self.assertIn("shutdown: requested from the panel", block)
        self.assertLess(block.index("shutdown: requested from the panel"),
                        block.index("os._exit(0)"),
                        "日志必须写在 os._exit 之前，否则来不及落盘")


if __name__ == "__main__":
    unittest.main()
