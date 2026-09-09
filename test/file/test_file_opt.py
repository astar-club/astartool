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


class TestReadLargeFile(unittest.TestCase):
    def test_streams_text_in_chunks(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "big.txt", "abcdefghij")
            chunks = list(file_opt.read_large_file(p, chunk_size=4))
            self.assertEqual(chunks, ["abcd", "efgh", "ij"])

    def test_reassembled_equals_full(self):
        with tempfile.TemporaryDirectory() as d:
            content = "line1\nline2\nline3\n"
            p = _write(d, "big.txt", content)
            reassembled = "".join(file_opt.read_large_file(p, chunk_size=3))
            self.assertEqual(reassembled, content)

    def test_bytes_mode_streams_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "big.bin")
            with open(p, "wb") as f:
                f.write(b"1234567890")
            chunks = list(file_opt.read_large_file(p, chunk_size=4, mode="bytes"))
            self.assertEqual(chunks, [b"1234", b"5678", b"90"])

    def test_not_a_file_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileOptError) as ctx:
                list(file_opt.read_large_file(os.path.join(d, "nope.txt")))
            self.assertEqual(ctx.exception.code, "not_a_file")


class TestWriteLargeFile(unittest.TestCase):
    def test_writes_iterable_in_chunks(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.txt")
            written = file_opt.write_large_file(
                p, ("ab", "cd", "ef"), chunk_size=2)
            self.assertEqual(written, 6)
            with open(p, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "abcdef")

    def test_writes_single_str_in_chunks(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.txt")
            written = file_opt.write_large_file(
                p, "abcdefghij", chunk_size=4)
            self.assertEqual(written, 10)
            with open(p, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "abcdefghij")

    def test_bytes_mode(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.bin")
            written = file_opt.write_large_file(
                p, [b"12", b"34"], mode="bytes", chunk_size=2)
            self.assertEqual(written, 4)
            with open(p, "rb") as f:
                self.assertEqual(f.read(), b"1234")

    def test_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sub", "deep", "out.txt")
            file_opt.write_large_file(p, "x")
            self.assertTrue(os.path.isfile(p))


class TestReadFileBytes(unittest.TestCase):
    def test_bytes_mode_returns_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.txt")
            with open(p, "wb") as f:
                f.write(b"l1\nl2\n")
            data = file_opt.read_file(p, mode="bytes")
            self.assertIsInstance(data, bytes)
            self.assertEqual(data, b"l1\nl2\n")

    def test_binary_does_not_decode(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.bin")
            with open(p, "wb") as f:
                f.write("\u4e2d\u6587".encode("utf-8"))
            # 任意非 "str" 的 mode 都按二进制读取
            data = file_opt.read_file(p, mode="binary")
            self.assertIsInstance(data, bytes)


class TestWriteFile(unittest.TestCase):
    def test_write_returns_char_count(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.txt")
            n = file_opt.write_file(p, "hello\nworld")
            self.assertEqual(n, len("hello\nworld"))
            with open(p, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "hello\nworld")

    def test_write_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sub", "deep", "out.txt")
            file_opt.write_file(p, "x")
            self.assertTrue(os.path.isfile(p))

    def test_write_binary_mode(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.bin")
            n = file_opt.write_file(p, b"\x00\x01\x02", mode="bytes")
            self.assertEqual(n, 3)
            with open(p, "rb") as f:
                self.assertEqual(f.read(), b"\x00\x01\x02")

    def test_write_binary_rejects_str(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.bin")
            with self.assertRaises(FileOptError) as ctx:
                file_opt.write_file(p, "not bytes", mode="bytes")
            self.assertEqual(ctx.exception.code, "type_error")

    def test_write_text_rejects_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "out.txt")
            with self.assertRaises(FileOptError) as ctx:
                file_opt.write_file(p, b"not str")
            self.assertEqual(ctx.exception.code, "type_error")


class TestListDir(unittest.TestCase):
    def test_lists_files_and_dirs_sorted(self):
        with tempfile.TemporaryDirectory() as d:
            os.mkdir(os.path.join(d, "zeta"))
            _write(d, "alpha.txt", "1")
            _write(d, "beta.txt", "2")
            entries = file_opt.list_dir(d)
            names = [e["name"] for e in entries]
            self.assertEqual(names, ["alpha.txt", "beta.txt", "zeta"])
            types = {e["name"]: e["type"] for e in entries}
            self.assertEqual(types["alpha.txt"], "file")
            self.assertEqual(types["zeta"], "dir")

    def test_not_a_dir_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "f.txt", "1")
            with self.assertRaises(FileOptError) as ctx:
                file_opt.list_dir(p)
            self.assertEqual(ctx.exception.code, "not_a_dir")


class TestSearchContent(unittest.TestCase):
    def test_finds_substring(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.txt", "apple\nbanana\ncherry")
            out = file_opt.search_content("banana", d)
            self.assertIn("banana", out)

    def test_no_match_returns_no_matches(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.txt", "apple\nbanana")
            out = file_opt.search_content("zzz_not_found", d)
            self.assertEqual(out, "(no matches)")


class TestListArchive(unittest.TestCase):
    def test_unsupported_not_archive_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "plain.txt", "not an archive")
            with self.assertRaises(FileOptError) as ctx:
                file_opt.list_archive(p)
            self.assertIn(ctx.exception.code, ("unsupported_archive", "archive_error"))


class TestEditFileMissingArgs(unittest.TestCase):
    def test_missing_args_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "c.py", "x\n")
            with self.assertRaises(FileOptError) as ctx:
                file_opt.edit_file(p)
            self.assertEqual(ctx.exception.code, "missing_argument")


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
