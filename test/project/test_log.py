import logging
import unittest
from collections import OrderedDict
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

import astartool.project._log as logmod
from astartool.project._log import (
    std_logging,
    file_logging,
    _format_template,
    _bind_arguments,
    _render_call,
)


class _Recorder:
    """A callable sink that records every call as (level, name, message)."""

    def __init__(self):
        self.calls = []

    def __call__(self, level, name, message):
        self.calls.append((level, name, message))


class TestBindArguments(unittest.TestCase):
    def test_positional(self):
        @std_logging()
        def foo(x, y):
            return 0

        # wrapt decorator -> wrapped is the original function via __wrapped__
        bound = _bind_arguments(foo.__wrapped__, (1, 2), {})
        self.assertEqual(dict(bound), {"x": 1, "y": 2})

    def test_keyword(self):
        @std_logging()
        def foo(x, y):
            return 0

        bound = _bind_arguments(foo.__wrapped__, (), {"x": 1, "y": 2})
        self.assertEqual(dict(bound), {"x": 1, "y": 2})

    def test_mixed_with_default(self):
        @std_logging()
        def foo(x, y, z=9):
            return 0

        bound = _bind_arguments(foo.__wrapped__, (1,), {"y": 2})
        self.assertEqual(dict(bound), {"x": 1, "y": 2, "z": 9})


class TestRenderCall(unittest.TestCase):
    def test_positional_only(self):
        self.assertEqual(_render_call("foo", OrderedDict([("x", 1), ("y", 2)])), "foo(1, 2)")

    def test_keyword_only(self):
        self.assertEqual(_render_call("foo", OrderedDict([("x", 1)])), "foo(1)")

    def test_empty(self):
        self.assertEqual(_render_call("foo", OrderedDict()), "foo()")


class TestFormatTemplate(unittest.TestCase):
    def test_named_fields(self):
        out = _format_template(
            "-> {name} {event} @ {level}",
            {"level": "INFO", "name": "foo", "event": "enter", "message": "enter foo()"},
        )
        self.assertEqual(out, "-> foo enter @ INFO")

    def test_positional_fields(self):
        out = _format_template(
            "call {} at {}",
            {"level": "INFO", "name": "foo", "event": "enter", "message": "enter foo()"},
        )
        self.assertEqual(out, "call foo at INFO")

    def test_mixed_fields(self):
        out = _format_template(
            "{}: {event}",
            {"level": "INFO", "name": "foo", "event": "exit", "message": "exit foo()"},
        )
        self.assertEqual(out, "foo: exit")

    def test_param_name_field(self):
        # Templates can reference the decorated function's parameter names
        out = _format_template(
            "{name}({x}, {y})",
            {"name": "foo", "x": 1, "y": 2},
        )
        self.assertEqual(out, "foo(1, 2)")

    def test_unknown_named_field_is_empty(self):
        out = _format_template("{name} {bad}", {"name": "foo"})
        self.assertEqual(out, "foo ")

    def test_malformed_template_does_not_raise(self):
        out = _format_template("{name} {", {"name": "foo"})
        self.assertEqual(out, "{name} {")


class TestStdLoggingDefault(unittest.TestCase):
    def test_default_prints_enter_and_exit_no_args(self):
        @std_logging(level=logging.INFO)
        def foo():
            return 42

        buf = StringIO()
        with redirect_stdout(buf):
            result = foo()
        self.assertEqual(result, 42)
        text = buf.getvalue()
        self.assertIn("[INFO]: enter foo()", text)
        self.assertIn("[INFO]: exit foo()", text)

    def test_default_prints_empty_parens_with_args(self):
        # Compatible with old version: always empty parentheses, args not shown
        @std_logging(level=logging.INFO)
        def foo(x, y):
            return x + y

        buf = StringIO()
        with redirect_stdout(buf):
            foo(1, 2)
        text = buf.getvalue()
        self.assertIn("[INFO]: enter foo()", text)
        self.assertIn("[INFO]: exit foo()", text)


class TestStdLoggingCallable(unittest.TestCase):
    def test_callable_sink_receives_message(self):
        rec = _Recorder()

        @std_logging(level=logging.INFO, on_enter=rec, on_exit=rec)
        def bar(x, y):
            return x * 2

        self.assertEqual(bar(3, 4), 6)
        self.assertEqual(len(rec.calls), 2)
        # Default message keeps empty parentheses, args not embedded
        self.assertEqual(rec.calls[0], ("INFO", "bar", "enter bar()"))
        self.assertEqual(rec.calls[1], ("INFO", "bar", "exit bar()"))

    def test_callable_sink_only_on_enter(self):
        rec = _Recorder()

        @std_logging(level=logging.INFO, on_enter=rec)
        def baz():
            return "ok"

        with redirect_stdout(StringIO()):
            self.assertEqual(baz(), "ok")
        self.assertEqual(len(rec.calls), 1)
        self.assertEqual(rec.calls[0][1], "baz")


class TestStdLoggingTemplate(unittest.TestCase):
    def test_param_name_template(self):
        # The key feature: reference function parameter names directly
        @std_logging(level=logging.INFO, on_enter="foo({x},{y})")
        def foo(x, y):
            return 1

        buf = StringIO()
        with redirect_stdout(buf):
            foo(1, y=2)
        self.assertIn("[INFO]: foo(1,2)", buf.getvalue())

    def test_named_template(self):
        @std_logging(level=logging.INFO, on_enter="-> {name} {event}",
                     on_exit="<- {name} {event}")
        def foo():
            return 1

        buf = StringIO()
        with redirect_stdout(buf):
            foo()
        text = buf.getvalue()
        self.assertIn("[INFO]: -> foo enter", text)
        self.assertIn("[INFO]: <- foo exit", text)

    def test_positional_template(self):
        @std_logging(level=logging.INFO, on_enter="call {} at {}")
        def foo():
            return 1

        buf = StringIO()
        with redirect_stdout(buf):
            foo()
        self.assertIn("[INFO]: call foo at INFO", buf.getvalue())


class TestFileLoggingDefault(unittest.TestCase):
    def test_default_logging(self):
        with mock.patch.object(logging, "getLogger") as mock_get:
            mock_logger = mock_get.return_value
            @file_logging(level=logging.INFO)
            def foo(x, y):
                return 7

            self.assertEqual(foo(1, 2), 7)
            self.assertEqual(mock_logger.log.call_count, 2)
            self.assertEqual(mock_logger.log.call_args_list[0][0][0], logging.INFO)
            self.assertEqual(mock_logger.log.call_args_list[0][0][1], "enter foo()")
            self.assertEqual(mock_logger.log.call_args_list[1][0][1], "exit foo()")
            # uses the module-level logger name
            mock_get.assert_called_with(logmod.__name__)


class TestFileLoggingCallable(unittest.TestCase):
    def test_callable_sink(self):
        rec = _Recorder()

        @file_logging(level="DEBUG", on_enter=rec, on_exit=rec)
        def foo():
            return None

        foo()
        self.assertEqual(len(rec.calls), 2)
        self.assertEqual(rec.calls[0][0], logging.DEBUG)


class TestFileLoggingTemplate(unittest.TestCase):
    def test_template_rendered_then_logged(self):
        with mock.patch.object(logging, "getLogger") as mock_get:
            mock_logger = mock_get.return_value
            @file_logging(level=logging.INFO, on_enter="enter {name}")
            def foo():
                return 1

            foo()
            self.assertEqual(mock_logger.log.call_args_list[0][0][1], "enter foo")

    def test_template_references_param(self):
        with mock.patch.object(logging, "getLogger") as mock_get:
            mock_logger = mock_get.return_value
            @file_logging(level=logging.INFO, on_enter="{name}({x})")
            def foo(x):
                return 1

            foo(5)
            self.assertEqual(mock_logger.log.call_args_list[0][0][1], "foo(5)")


class TestInvalidTemplateSafe(unittest.TestCase):
    def test_bad_template_does_not_break_function(self):
        @std_logging(level=logging.INFO, on_enter="{name} {")
        def foo():
            return "value"

        buf = StringIO()
        with redirect_stdout(buf):
            self.assertEqual(foo(), "value")


if __name__ == "__main__":
    unittest.main()
