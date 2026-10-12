import tempfile
import unittest
from pathlib import Path
from unittest import mock

from astartool.project._project import (
    file_to_lines,
    walk,
    project_to_lines,
    project_to_pdf,
    _compress_blank_lines_in_file,
    _paginate_lines,
    _confirm_remove,
    _resolve_pdf_path,
)

try:
    import reportlab  # noqa: F401
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class ProjectTestCase(unittest.TestCase):
    """公共工具：构造临时源码工程。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def write(self, relpath, content):
        path = self.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding='utf-8')
        return path


class TestFileToLines(ProjectTestCase):
    def test_returns_source_line_count(self):
        src = self.write('a.py', 'line1\nline2\nline3\n')
        out = self.root / 'out.txt'
        count = file_to_lines(src, to_file=str(out))
        self.assertEqual(count, 3)

    def test_returns_zero_for_binary_file(self):
        src = self.root / 'bin.py'
        src.write_bytes(b'\xff\xfe\x00\x81')
        out = self.root / 'out.txt'
        count = file_to_lines(src, to_file=str(out))
        self.assertEqual(count, 0)


class TestCompressBlankLines(ProjectTestCase):
    def test_compress_consecutive_blanks_keep_one(self):
        path = self.write('t.txt',
                          '\n\na\n\n\n\nb\n\n\nc\n\n\n')
        _compress_blank_lines_in_file(path)
        lines = path.read_text(encoding='utf-8').splitlines()
        self.assertEqual(lines, ['a', '', 'b', '', 'c'])

    def test_compress_max_blank_zero_removes_all(self):
        path = self.write('t.txt', 'a\n\n\nb\n')
        _compress_blank_lines_in_file(path, max_blank=0)
        lines = path.read_text(encoding='utf-8').splitlines()
        self.assertEqual(lines, ['a', 'b'])

    def test_strip_leading_and_trailing_blanks(self):
        path = self.write('t.txt', '\n\na\nb\n\n\n')
        _compress_blank_lines_in_file(path)
        text = path.read_text(encoding='utf-8')
        self.assertFalse(text.startswith('\n'))
        self.assertFalse(text.endswith('\n\n'))


class TestProjectToLines(ProjectTestCase):
    def _make_project(self):
        self.write('pkg/a.py', 'a1\n\n\n\na2\n')          # 5 lines incl. blanks
        self.write('pkg/sub/b.py', 'b1\n\n\nb2\n')        # 4 lines incl. blanks
        self.write('data.bin', b'\xff\xfe\x00')           # 后缀不过滤
        self.write('README.md', 'not source\n')           # 后缀不过滤

    def test_stats_counts_files_and_lines(self):
        self._make_project()
        out = self.root / 'out.txt'
        stats = project_to_lines(
            src_project=str(self.root), to_file=str(out))
        self.assertEqual(stats['file_count'], 2)
        # a.py: 5 行；b.py: 4 行（均含源码自身空行）
        self.assertEqual(stats['source_lines'], 9)

    def test_blank_lines_compressed(self):
        self._make_project()
        out = self.root / 'out.txt'
        project_to_lines(src_project=str(self.root), to_file=str(out))
        lines = out.read_text(encoding='utf-8').splitlines()
        # 无连续两个空行
        for prev, cur in zip(lines, lines[1:]):
            self.assertFalse(prev.strip() == '' and cur.strip() == '',
                             'unexpected consecutive blank lines')
        # 无首尾空行
        self.assertNotEqual(lines[0].strip(), '')
        self.assertNotEqual(lines[-1].strip(), '')
        # 每个源码文件之间保留 1 行空行分隔
        self.assertIn('', lines)

    def test_no_compression_when_disabled(self):
        self.write('a.py', 'a1\n\n\n\na2\n')
        out = self.root / 'out.txt'
        project_to_lines(src_project=str(self.root), to_file=str(out),
                         compress_blank=False)
        text = out.read_text(encoding='utf-8')
        self.assertIn('\n\n\n', text)

    def test_walk_returns_stats(self):
        self._make_project()
        out = self.root / 'out.txt'
        stats = walk(self.root, to_file=str(out))
        self.assertEqual(stats['file_count'], 2)
        self.assertEqual(stats['source_lines'], 9)

    def test_existing_target_removed_when_confirmed(self):
        self.write('pkg/a.py', 'a1\na2\n')
        out = self.root / 'out.txt'
        out.write_text('old content\n', encoding='utf-8')
        with mock.patch('builtins.input', return_value='Y'):
            stats = project_to_lines(src_project=self.root, to_file=out)
        # 确认后删除旧文件并正常导出
        self.assertEqual(stats['file_count'], 1)
        self.assertIn('a1', out.read_text(encoding='utf-8'))
        self.assertNotIn('old content', out.read_text(encoding='utf-8'))

    def test_existing_target_kept_when_declined(self):
        self.write('pkg/a.py', 'a1\na2\n')
        out = self.root / 'out.txt'
        out.write_text('old content\n', encoding='utf-8')
        with mock.patch('builtins.input', return_value='N'):
            stats = project_to_lines(src_project=self.root, to_file=out)
        # 拒绝删除时放弃导出，返回空统计且不覆盖原文件
        self.assertEqual(stats, {'file_count': 0, 'source_lines': 0})
        self.assertEqual(out.read_text(encoding='utf-8'), 'old content\n')

    def test_existing_target_kept_on_empty_input(self):
        self.write('pkg/a.py', 'a1\na2\n')
        out = self.root / 'out.txt'
        out.write_text('old content\n', encoding='utf-8')
        with mock.patch('builtins.input', return_value=''):
            stats = project_to_lines(src_project=self.root, to_file=out)
        # 空输入视为拒绝
        self.assertEqual(stats, {'file_count': 0, 'source_lines': 0})
        self.assertEqual(out.read_text(encoding='utf-8'), 'old content\n')

    def test_pathlib_path_arguments(self):
        # 路径参数同时接受 pathlib.Path（而非仅 str）
        self.write('pkg/a.py', 'a1\na2\n')
        out = self.root / 'out.txt'
        stats = project_to_lines(
            src_project=self.root, to_file=out)  # 均传 Path
        self.assertEqual(stats['file_count'], 1)
        self.assertEqual(stats['source_lines'], 2)
        # _compress_blank_lines_in_file 亦接受 Path
        _compress_blank_lines_in_file(out)
        self.assertEqual(out.read_text(encoding='utf-8').splitlines()[-1],
                         'a2')


class TestPaginate(unittest.TestCase):
    def test_paginate_even(self):
        pages = _paginate_lines(list(range(10)), 5)
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0], [0, 1, 2, 3, 4])
        self.assertEqual(pages[1], [5, 6, 7, 8, 9])

    def test_paginate_remainder(self):
        pages = _paginate_lines(list(range(7)), 5)
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[1], [5, 6])

    def test_paginate_empty_gives_one_page(self):
        pages = _paginate_lines([], 50)
        self.assertEqual(pages, [[]])


class TestResolvePdfPath(ProjectTestCase):
    def test_free_path_unchanged(self):
        path = self.root / 'x.pdf'
        self.assertEqual(_resolve_pdf_path(path), path)

    def test_existing_confirmed_returns_original(self):
        path = self.root / 'x.pdf'
        path.write_bytes(b'old')
        with mock.patch('builtins.input', return_value='Y'):
            resolved = _resolve_pdf_path(path)
        # 确认后删除旧文件并返回原路径
        self.assertEqual(resolved, path)
        self.assertFalse(path.exists())

    def test_existing_declined_returns_none(self):
        path = self.root / 'x.pdf'
        path.write_bytes(b'old')
        with mock.patch('builtins.input', return_value='N'):
            resolved = _resolve_pdf_path(path)
        # 拒绝删除：返回 None 且不动原文件
        self.assertIsNone(resolved)
        self.assertTrue(path.exists())
        self.assertEqual(path.read_bytes(), b'old')

    def test_existing_unlink_failure_falls_back_to_timestamp(self):
        path = self.root / 'x.pdf'
        path.write_bytes(b'old')
        with mock.patch('builtins.input', return_value='Y'), \
                mock.patch.object(Path, 'unlink',
                                  side_effect=PermissionError('occupied')):
            resolved = _resolve_pdf_path(path)
        # 确认删除但被占用：降级为时间戳文件名，原文件保留
        self.assertIsNotNone(resolved)
        self.assertNotEqual(resolved, path)
        self.assertTrue(resolved.name.startswith('x_'))
        self.assertTrue(resolved.name.endswith('.pdf'))
        self.assertTrue(path.exists())


class TestConfirmRemove(ProjectTestCase):
    def test_nonexistent_returns_true_without_prompt(self):
        with mock.patch('builtins.input',
                        side_effect=AssertionError('should not prompt')):
            self.assertTrue(_confirm_remove(self.root / 'nope.txt'))

    def test_existing_confirmed(self):
        path = self.root / 'a.txt'
        path.write_text('x', encoding='utf-8')
        with mock.patch('builtins.input', return_value='y'):
            self.assertTrue(_confirm_remove(path))

    def test_existing_declined(self):
        path = self.root / 'a.txt'
        path.write_text('x', encoding='utf-8')
        with mock.patch('builtins.input', return_value=''):
            self.assertFalse(_confirm_remove(path))


@unittest.skipUnless(HAS_REPORTLAB, 'reportlab not installed')
class TestProjectToPdf(ProjectTestCase):
    def _make_project(self, file_count=2, lines_each=10):
        for i in range(file_count):
            content = ''.join('code %d %d\n' % (i, j) for j in range(lines_each))
            self.write('pkg/mod_%d.py' % i, content)

    def test_pdf_generated_with_stats(self):
        self._make_project(file_count=2, lines_each=10)
        out_dir = self.root / 'out'
        info = project_to_pdf(
            src_project=str(self.root),
            to_dir=str(out_dir),
            software_name='TestSoft',
            version=(1, 0, 0, 'final', 0),
        )
        # txt 与 pdf 均生成
        self.assertTrue(info['txt'].exists())
        self.assertTrue(info['pdf'].exists())
        with info['pdf'].open('rb') as f:
            self.assertTrue(f.read(5).startswith(b'%PDF'))
        # 统计正确：2 个文件，每个 10 行
        self.assertEqual(info['file_count'], 2)
        self.assertEqual(info['source_lines'], 20)
        # 20 源码行 + 2 路径行 + 1 文件间空行 = 23 行 -> 1 页
        self.assertEqual(info['total_pages'], 1)
        # 未超过 60 页，软著提交版不拆分
        self.assertIsNone(info['pdf_part'])
        self.assertEqual(info['part_pages'], 1)

    def test_pdf_head_tail_split(self):
        # 3 个文件 x 100 行 = 300 源码行 + 3 路径行 + 2 空行 = 305 行
        # lines_per_page=10 -> 31 页 > max_pages=20 -> 拆分为前 3 + 后 3 页
        self._make_project(file_count=3, lines_each=100)
        out_dir = self.root / 'out'
        info = project_to_pdf(
            src_project=str(self.root),
            to_dir=str(out_dir),
            software_name='TestSoft',
            version='1.0',
            lines_per_page=10,
            keep_pages=3,
            max_pages=20,
        )
        self.assertGreater(info['total_pages'], 20)
        self.assertIsNotNone(info['pdf_part'])
        self.assertTrue(info['pdf_part'].exists())
        self.assertEqual(info['part_pages'], 6)
        self.assertIn('head3_tail3', info['pdf_part'].name)
        # 完整版仍然输出
        self.assertTrue(info['pdf'].exists())

    def test_existing_pdf_overwritten(self):
        self._make_project(file_count=1, lines_each=5)
        out_dir = self.root / 'out'
        out_dir.mkdir(parents=True)
        # 预先放置一个损坏的旧 PDF，确认后重新生成覆盖
        old = out_dir / 'source_code.pdf'
        old.write_bytes(b'not a pdf')
        with mock.patch('builtins.input', return_value='Y'):
            info = project_to_pdf(
                src_project=str(self.root),
                to_dir=str(out_dir),
                software_name='TestSoft',
            )
        with info['pdf'].open('rb') as f:
            self.assertTrue(f.read(5).startswith(b'%PDF'))

    def test_existing_pdf_declined_returns_empty(self):
        self._make_project(file_count=1, lines_each=5)
        out_dir = self.root / 'out'
        out_dir.mkdir(parents=True)
        old = out_dir / 'source_code.pdf'
        old.write_bytes(b'not a pdf')
        with mock.patch('builtins.input', return_value='N'):
            info = project_to_pdf(
                src_project=str(self.root),
                to_dir=str(out_dir),
                software_name='TestSoft',
            )
        # 拒绝删除已存在的完整版 PDF：放弃导出，旧 PDF 不动
        self.assertIsNone(info['pdf'])
        self.assertIsNone(info['pdf_part'])
        self.assertEqual(info['total_pages'], 0)
        self.assertEqual(old.read_bytes(), b'not a pdf')
        # 源码文本已生成（txt 的确认在 PDF 之前，此处 txt 原本不存在）
        self.assertTrue(info['txt'].exists())

    def test_existing_part_pdf_declined_keeps_full_only(self):
        # 31 页 > max_pages=20，会尝试生成软著提交版
        self._make_project(file_count=3, lines_each=100)
        out_dir = self.root / 'out'
        out_dir.mkdir(parents=True)
        part = out_dir / 'source_code_head3_tail3.pdf'
        part.write_bytes(b'old part')

        def _fake_input(prompt=''):
            # 完整版 PDF 不存在（返回 True 前不弹）；提交版已存在 -> 拒绝
            return 'N'

        with mock.patch('builtins.input', side_effect=_fake_input):
            info = project_to_pdf(
                src_project=str(self.root),
                to_dir=str(out_dir),
                software_name='TestSoft',
                lines_per_page=10,
                keep_pages=3,
                max_pages=20,
            )
        # 完整版正常生成，提交版被拒绝：pdf_part 为 None、part_pages 为 0
        self.assertIsNotNone(info['pdf'])
        self.assertTrue(info['pdf'].exists())
        self.assertIsNone(info['pdf_part'])
        self.assertEqual(info['part_pages'], 0)
        self.assertEqual(part.read_bytes(), b'old part')

    def test_existing_txt_confirmed_then_exported(self):
        self._make_project(file_count=1, lines_each=5)
        out_dir = self.root / 'out'
        out_dir.mkdir(parents=True)
        (out_dir / 'source_code.txt').write_text('old txt\n', encoding='utf-8')
        with mock.patch('builtins.input', return_value='Y'):
            info = project_to_pdf(
                src_project=str(self.root),
                to_dir=str(out_dir),
                software_name='TestSoft',
            )
        self.assertIsNotNone(info['pdf'])
        self.assertTrue(info['pdf'].exists())
        # 旧 txt 被删除后重新生成
        self.assertNotIn('old txt',
                         info['txt'].read_text(encoding='utf-8'))

    def test_existing_txt_declined_returns_empty(self):
        self._make_project(file_count=1, lines_each=5)
        out_dir = self.root / 'out'
        out_dir.mkdir(parents=True)
        (out_dir / 'source_code.txt').write_text('old txt\n', encoding='utf-8')
        with mock.patch('builtins.input', return_value='N'):
            info = project_to_pdf(
                src_project=str(self.root),
                to_dir=str(out_dir),
                software_name='TestSoft',
            )
        # 用户拒绝删除：放弃导出，pdf 为 None，旧 txt 不被覆盖
        self.assertIsNone(info['pdf'])
        self.assertIsNone(info['pdf_part'])
        self.assertEqual(info['total_pages'], 0)
        self.assertEqual(info['source_lines'], 0)
        self.assertEqual(info['txt'].read_text(encoding='utf-8'), 'old txt\n')
        self.assertFalse((out_dir / 'source_code.pdf').exists())


if __name__ == '__main__':
    unittest.main()
