import builtins
import importlib.util
import unittest

from astartool.file import imagehelper

_HAS_PIL = importlib.util.find_spec("PIL") is not None


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


class TestBase64ToImage(unittest.TestCase):
    def test_missing_pillow_raises(self):
        with _ImportBlocker("PIL"):
            with self.assertRaises(ImportError):
                imagehelper.base64_to_image("data:image/png;base64,xxx")

    @unittest.skipUnless(_HAS_PIL, "Pillow not installed")
    def test_decode_to_image(self):
        # 1x1 red pixel PNG
        b64 = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42m"
               "P8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
        img = imagehelper.base64_to_image("data:image/png;base64," + b64)
        self.assertEqual(img.size, (1, 1))


if __name__ == "__main__":
    unittest.main()
