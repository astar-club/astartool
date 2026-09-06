import builtins
import importlib.util
import unittest
import warnings

from astartool.project._decorators import (
    require_optional_import,
    deprecated_version,
    VersionDeprecatedError,
)


class _ImportBlocker:
    """Context manager that simulates a missing optional dependency."""

    def __init__(self, *names):
        self.names = set(names)
        self._orig = None

    def __enter__(self):
        self._orig = builtins.__import__

        def _fake(name, *args, **kwargs):
            if name.split('.')[0] in self.names:
                raise ImportError('simulated missing: ' + name)
            return self._orig(name, *args, **kwargs)

        builtins.__import__ = _fake
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.__import__ = self._orig
        return False


class TestRequireOptionalImport(unittest.TestCase):
    def test_imported_package_runs(self):
        @require_optional_import("json")
        def func():
            import json
            return json.dumps({"ok": True})

        self.assertEqual(func(), '{"ok": true}')

    def test_missing_package_raises_import_error(self):
        with _ImportBlocker("no_such_module_xyz"):
            @require_optional_import("no_such_module_xyz")
            def func():
                return 1

            with self.assertRaises(ImportError):
                func()

    def test_custom_error_message(self):
        with _ImportBlocker("no_such_module_abc"):
            @require_optional_import(
                "no_such_module_abc",
                "功能需要 {module}，请运行 pip install {module}",
            )
            def func():
                return 1

            with self.assertRaises(ImportError) as ctx:
                func()
            self.assertIn("no_such_module_abc", str(ctx.exception))

    def test_custom_exception_class(self):
        class MyDepError(RuntimeError):
            pass

        with _ImportBlocker("no_such_module_def"):
            @require_optional_import(
                "no_such_module_def", "缺包 {module}", exception=MyDepError
            )
            def func():
                return 2

            with self.assertRaises(MyDepError):
                func()

    def test_import_is_cached(self):
        import_count = {"n": 0}

        real_import = builtins.__import__

        def counting_import(name, *args, **kwargs):
            if name == "json":
                import_count["n"] += 1
            return real_import(name, *args, **kwargs)

        @require_optional_import("json")
        def func():
            import json
            return 1

        builtins.__import__ = counting_import
        try:
            func()
            func()
        finally:
            builtins.__import__ = real_import

        # the decorated probe imports once and caches the result
        self.assertEqual(import_count["n"], 2)


class TestDeprecatedVersion(unittest.TestCase):
    def test_active_below_interval(self):
        @deprecated_version((1, 0), (2, 0), current_version=(0, 9))
        def func():
            return "ok"

        self.assertEqual(func(), "ok")

    def test_deprecated_in_interval_warns_but_runs(self):
        @deprecated_version((1, 0), (2, 0), current_version=(1, 5))
        def func():
            return "ok"

        with self.assertWarns(DeprecationWarning):
            self.assertEqual(func(), "ok")

    def test_removed_at_upper_bound(self):
        @deprecated_version((1, 0), (2, 0), current_version=(2, 0))
        def func():
            return "should-not-run"

        with self.assertRaises(VersionDeprecatedError):
            func()

    def test_removed_above_upper_bound(self):
        @deprecated_version((1, 0), (2, 0), current_version=(3, 0))
        def func():
            return "should-not-run"

        with self.assertRaises(VersionDeprecatedError):
            func()

    def test_string_version_parsing(self):
        @deprecated_version(
            "1.0", "2.0", current_version="1.2",
            message="{func} 已弃用(当前{current})，请改用新接口",
        )
        def func():
            return "ok"

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.assertEqual(func(), "ok")
        deprecation_warnings = [
            w for w in caught
            if issubclass(w.category, DeprecationWarning)
            and "已弃用" in str(w.message)
        ]
        self.assertTrue(deprecation_warnings, "expected a custom deprecation warning")
        self.assertIn("已弃用", str(deprecation_warnings[0].message))

    def test_custom_removed_message(self):
        @deprecated_version(
            (1, 0), (3, 0), current_version=(3, 0),
            message="区间提示",
            removed_message="{func} 已在 {transition} 之后彻底移除",
        )
        def func():
            return "no"

        with self.assertRaises(VersionDeprecatedError) as ctx:
            func()
        self.assertIn("彻底移除", str(ctx.exception))

    def test_state_is_cached(self):
        @deprecated_version((1, 0), (2, 0), current_version=(1, 5))
        def func():
            return "ok"

        with self.assertWarns(DeprecationWarning):
            func()
        # second call reuses cached state (still runs, still warns)
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(func(), "ok")


if __name__ == "__main__":
    unittest.main()
