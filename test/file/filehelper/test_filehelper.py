import pathlib
import unittest

from astartool.file.filehelper import is_file_using, release_and_delete_file, release_lock


class FileHelperTest(unittest.TestCase):
    def setUp(self) -> None:
        base_path = pathlib.Path(__file__).parent.parent
        path = base_path / "demo_data"

        self.zip_path = path / "demo_compresshelper.zip"
        self.rar_path = path / "demo_compresshelper.rar"
        self.tar_path = path / "demo_compresshelper.tar"
        self.tar_bz2_path = path / "demo_compresshelper.tar.bz2"
        self.tar_gz_path = path / "demo_compresshelper.tar.gz"
        self.tar_xz_path = path / "demo_compresshelper.tar.xz"

    def test_file_is_using(self):

        f = self.zip_path.open()
        self.assertTrue(is_file_using(str(self.zip_path.absolute())))
        f.close()
        self.assertFalse(is_file_using(str(self.zip_path.absolute())))
