import pathlib
import unittest

from astartool.setuptool import _tool
from astartool.file import file_opt

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


class TestReadFileConsistent(unittest.TestCase):
    def test_readme_consistency(self):
        # setuptool.read_file delegates to file_opt.read_file -> identical result
        r_tool = _tool.read_file(str(BASE_DIR / "README.md"))
        r_opt = file_opt.read_file(str(BASE_DIR / "README.md"))
        self.assertEqual(r_tool, r_opt)

    def test_trailing_newline_preserved(self):
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.txt")
            content = "line1\nline2\nline3\n"
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            self.assertEqual(_tool.read_file(p), content)
            self.assertEqual(file_opt.read_file(p), content)

    def test_no_trailing_newline(self):
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "b.txt")
            content = "foo\nbar\nbaz"
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            self.assertEqual(_tool.read_file(p), content)
            self.assertEqual(file_opt.read_file(p), content)


class TestLoadInstallRequires(unittest.TestCase):
    def test_main_has_no_optional(self):
        reqs = _tool.load_install_requires()
        self.assertNotIn("numpy>=1.0.1", reqs)
        self.assertNotIn("rarfile", reqs)
        self.assertNotIn("xlwt", reqs)
        self.assertNotIn("openpyxl", reqs)
        self.assertNotIn("pillow", reqs)
        # required deps still present
        self.assertTrue(any("snowland-smx" in r for r in reqs))

    def test_optional_section(self):
        reqs = _tool.load_install_requires(extra="optional")
        self.assertIn("numpy>=1.0.1", reqs)
        self.assertIn("rarfile", reqs)
        self.assertIn("xlwt", reqs)
        self.assertIn("xlrd", reqs)
        self.assertIn("openpyxl", reqs)
        self.assertIn("pillow", reqs)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            _tool.load_install_requires(filepath="no_such_requirements.txt")


if __name__ == "__main__":
    unittest.main()
