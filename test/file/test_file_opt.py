import os
import tempfile
import unittest

from astartool.file import file_opt
from astartool.error.file_opt_error import FileOptError


def _write(tmp_dir, name, content):
    p = os.path.join(tmp_dir, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class TestReadFile(unittest.TestCase):
    def test_full_read_preserves_newline(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "a.txt", "l1\nl2\nl3\n")
            self.assertEqual(file_opt.read_file(p), "l1\nl2\nl3\n")

    def test_line_slice(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "a.txt", "l1\nl2\nl3\n")
            self.assertEqual(file_opt.read_file(p, start="1", end="2"), "l2\n")

    def test_limit(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "a.txt", "l1\nl2\nl3\n")
            self.assertEqual(file_opt.read_file(p, start="0", end="end", limit=2), "l1\nl2\n")

    def test_nonexistent_raises(self):
        with self.assertRaises(FileOptError):
            file_opt.read_file(os.path.join("no", "such", "file.txt"))


class TestEditFile(unittest.TestCase):
    def test_multi_replace(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "c.py", "def foo():\n    return 1\n")
            res = file_opt.edit_file(
                p, old=["def foo():", "return 1"],
                new=["def bar():", "return 2"],
            )
            self.assertEqual(res["mode"], "replace")
            with open(p, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "def bar():\n    return 2\n")

    def test_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "c.py", "old content\n")
            res = file_opt.edit_file(p, content="# rewritten\n")
            self.assertEqual(res["mode"], "overwrite")
            with open(p, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "# rewritten\n")

    def test_no_match_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "c.py", "x\n")
            with self.assertRaises(FileOptError) as ctx:
                file_opt.edit_file(p, old=["nope"], new=["yep"])
            self.assertEqual(ctx.exception.code, "edit_no_match")

    def test_length_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "c.py", "x\n")
            with self.assertRaises(FileOptError) as ctx:
                file_opt.edit_file(p, old=["a", "b"], new=["c"])
            self.assertEqual(ctx.exception.code, "length_mismatch")


if __name__ == "__main__":
    unittest.main()
