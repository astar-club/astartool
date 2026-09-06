import builtins
import importlib.util
import pathlib
import unittest

from astartool.file import compresshelper

_BASE = pathlib.Path(__file__).resolve().parent / "demo_data"
_RAR_PATH = _BASE / "demo_compresshelper.rar"

_HAS_RARFILE = importlib.util.find_spec("rarfile") is not None


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


class TestRarfileLazyImport(unittest.TestCase):
    def test_missing_rarfile_raises_in_namelist(self):
        with _ImportBlocker("rarfile"):
            with self.assertRaises(ImportError):
                compresshelper.namelist(str(_RAR_PATH))

    def test_missing_rarfile_raises_in_extract(self):
        with _ImportBlocker("rarfile"):
            with self.assertRaises(ImportError):
                compresshelper.extractall_from_rar(str(_RAR_PATH), "out_dir")

    @unittest.skipUnless(_HAS_RARFILE, "rarfile not installed")
    def test_namelist_rar_works(self):
        names = compresshelper.namelist(str(_RAR_PATH), sort=True)
        self.assertIsInstance(names, list)
        self.assertTrue(len(names) > 0)


if __name__ == "__main__":
    unittest.main()
