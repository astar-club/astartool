import builtins
import importlib.util
import os
import tempfile
import unittest

from astartool.file import excelhelper


class _ImportBlocker:
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

    def __exit__(self, *a):
        builtins.__import__ = self._orig
        return False


_HAS_XLWT = importlib.util.find_spec("xlwt") is not None
_HAS_OPENPYXL = importlib.util.find_spec("openpyxl") is not None


class TestToExcelDispatch(unittest.TestCase):
    def test_xls_suffix_uses_xlwt(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.xls")
            excelhelper.to_excel(
                [{"name": "a", "age": 1}],
                p, sheetname="s", fields=["name", "age"],
                output_fields=["Name", "Age"],
            )
            self.assertTrue(os.path.exists(p))

    @unittest.skipUnless(_HAS_XLWT, "xlwt not installed")
    def test_xls_multi_sheet(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "multi.xls")
            excelhelper.to_excel(
                [[{"a": 1}], [{"a": 2}]],
                p, sheetname=["s1", "s2"],
                fields=[["a"], ["a"]], output_fields=[["A"], ["A"]],
            )
            import xlrd
            book = xlrd.open_workbook(p)
            self.assertEqual(book.sheet_names(), ["s1", "s2"])

    @unittest.skipUnless(_HAS_OPENPYXL, "openpyxl not installed")
    def test_xlsx_suffix_uses_openpyxl(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.xlsx")
            excelhelper.to_excel(
                [{"name": "a", "age": 1}],
                p, sheetname="s", fields=["name", "age"],
                output_fields=["Name", "Age"],
            )
            import openpyxl
            wb = openpyxl.load_workbook(p)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            self.assertEqual(rows[0], ("Name", "Age"))

    def test_missing_xlwt_raises(self):
        with _ImportBlocker("xlwt"):
            with self.assertRaises(ImportError):
                excelhelper.to_excel([{"a": 1}], "out.xls",
                                      fields=["a"], output_fields=["A"])

    def test_missing_openpyxl_raises(self):
        with _ImportBlocker("openpyxl"):
            with self.assertRaises(ImportError):
                excelhelper.to_excel([{"a": 1}], "out.xlsx",
                                      fields=["a"], output_fields=["A"])


if __name__ == "__main__":
    unittest.main()
