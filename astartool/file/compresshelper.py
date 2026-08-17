#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: filehelper.py
# @time: 2024/9/2 17:33
# @Software: PyCharm


import enum
import os
import pathlib
import tarfile
import zipfile
from typing import Union

from astartool.error import ParameterValueError, ParameterTypeError


def _require_rarfile():
    """
    Lazily import the optional ``rarfile`` dependency.

    :raises ImportError: if ``rarfile`` is not installed.
    :return: the ``rarfile`` module.
    """
    try:
        import rarfile
    except ImportError:
        raise ImportError(
            "rarfile is required to handle RAR archives. Install it via "
            "`pip install rarfile` or `pip install astartool[optional]`."
        )
    return rarfile


class CompressionType(enum.Enum):
    ZIP = "zip"
    GZIP = "gz"
    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"
    BZ2 = "bz2"
    LZMA = "lzma"
    XZ = "xz"
    RAR = "rar"


SUFFIX_LIST = [".zip", '.gz', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.bz2', '.lzma', '.xz', '.rar']


def get_compression_type_by_file_name(filename):
    """
    通过文件名获取压缩类型
    :param filename:
    :return:
    """
    path = pathlib.Path(filename)
    suffixes = path.suffixes
    suffixes_1 = suffixes[-1].lower()
    if suffixes_1 in SUFFIX_LIST:
        if suffixes_1 in ('.bz2', '.gz', '.xz') and (len(suffixes) >= 2 and suffixes[-2].lower() == ".tar"):
            return CompressionType("tar{}".format(suffixes_1))
        else:
            return CompressionType(suffixes_1[1:])
    raise ParameterValueError("Error: Suffixes of `filename` must in `SUFFIX_LIST`")


def namelist(filepath: Union[str, pathlib.Path], sort: bool=True):
    """
    zip/rar/tar文件名列表
    :param filepath: str/Path 文件路径
    :param sort: 返回列表是否按字典序
    :return:
    """
    try:
        compression_type = get_compression_type_by_file_name(filepath)
        if compression_type == CompressionType.ZIP:
            z = zipfile.ZipFile(filepath, "r")
            li = z.namelist()
            if sort:
                li.sort()
            z.close()
            return li
        elif compression_type == CompressionType.RAR:
            rarfile = _require_rarfile()
            z = rarfile.RarFile(filepath, "r")
            li = z.namelist()
            li = [each for each in li if not each.endswith("/")]
            if sort:
                li.sort()
            z.close()
            return li
        elif compression_type == CompressionType.TAR:
            z = tarfile.open(filepath, "r")
            li = [item.name for item in z.getmembers() if not item.isdir()]
            if sort:
                li.sort()
            z.close()
            return li
        elif compression_type == CompressionType.TAR_GZ:
            z = tarfile.open(filepath, "r:gz")
            li = [item.name for item in z.getmembers() if not item.isdir()]
            if sort:
                li.sort()
            z.close()
            return li
        elif compression_type == CompressionType.TAR_BZ2:
            z = tarfile.open(filepath, "r:bz2")
            li = [item.name for item in z.getmembers() if not item.isdir()]
            if sort:
                li.sort()
            z.close()
            return li
        elif compression_type == CompressionType.TAR_XZ:
            z = tarfile.open(filepath, "r:xz")
            li = [item.name for item in z.getmembers() if not item.isdir()]
            if sort:
                li.sort()
            z.close()
            return li
        elif compression_type == CompressionType.RAR:
            rarfile = _require_rarfile()
            z = rarfile.RarFile(filepath)
            li = z.namelist()
            if sort:
                li.sort()
            z.close()
            return li
        else:
            raise ParameterValueError("Error: File type `{}` is not supported.".format(compression_type))
    except ParameterValueError as e:
        raise e


def extractall_from_zip(zip_path, target_dir, file_names=None, password=None, encoding='utf-8'):
    """
    解压文件夹
    :param zip_path:
    :param target_dir:
    :param file_names:
    :param password:
    :return:
    """
    if password and isinstance(password, str):
        password = bytes(password, encoding=encoding)
    if password and not isinstance(password, bytes):
        raise ParameterTypeError("Error type: Type of `password` must be string or bytes.")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(target_dir, file_names, password)


def extractall_from_rar(rar_path, target_dir, file_names=None, password=None, encoding='utf-8'):
    """
    解压文件夹
    :param rar_path:
    :param target_dir:
    :param file_names:
    :param password:
    :return:
    """
    if password and isinstance(password, str):
        password = bytes(password, encoding=encoding)
    if password and not isinstance(password, bytes):
        raise ParameterTypeError("Error type: Type of `password` must be string or bytes.")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    rarfile = _require_rarfile()
    with rarfile.RarFile(rar_path, 'r') as r:
        r.extractall(target_dir, file_names, password)


def extractall_from_tar(tar_path, target_dir, file_names=None, password=None, extra=None, encoding='utf-8'):
    """
    解压文件夹
    :param tar_path:
    :param target_dir:
    :param file_names:
    :return:
    """

    if password and isinstance(password, str):
        password = bytes(password, encoding=encoding)
    if password and not isinstance(password, bytes):
        raise ParameterTypeError("Error type: Type of `password` must be string or bytes.")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if extra:
        with tarfile.open(tar_path, 'r:{}'.format(extra)) as r:
            file_names = [(r.getmember(f) if isinstance(f, str) else f) for f in file_names]
            r.extractall(target_dir, file_names)
    else:
        with tarfile.TarFile(tar_path, 'r') as r:
            file_names = [(r.getmember(f) if isinstance(f, str) else f) for f in file_names]
            r.extractall(target_dir, file_names)


def extractall_from_tar_gz(tar_path, target_dir, file_names=None, password=None, encoding='utf-8'):
    """
    解压文件夹
    :param tar_path:
    :param target_dir:
    :param file_names:
    :return:
    """
    return extractall_from_tar(tar_path, target_dir, file_names, password, extra="gz", encoding=encoding)


def extractall_from_tar_bz2(tar_path, target_dir, file_names=None, password=None, encoding='utf-8'):
    """
    解压文件夹
    :param tar_path:
    :param target_dir:
    :param file_names:
    :return:
    """
    return extractall_from_tar(tar_path, target_dir, file_names, password=None, extra="bz2", encoding=encoding)


def extractall_from_tar_xz(tar_path, target_dir, file_names=None, password=None, encoding='utf-8'):
    """
    解压文件夹
    :param tar_path:
    :param target_dir:
    :param file_names:
    :return:
    """
    return extractall_from_tar(tar_path, target_dir, file_names, password, extra="xz", encoding=encoding)


def extractall(filepath, target_dir, file_names=None, password=None, encoding='utf-8'):
    """

    :param filepath:
    :param target_dir:
    :param file_names:
    :return:
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    compression_type = get_compression_type_by_file_name(filepath)
    if compression_type == CompressionType.ZIP:
        extractall_from_zip(filepath, target_dir, file_names, password, encoding=encoding)
    elif compression_type == CompressionType.RAR:
        extractall_from_rar(filepath, target_dir, file_names, password, encoding=encoding)
    elif compression_type == CompressionType.TAR:
        extractall_from_tar(filepath, target_dir, file_names, password, encoding=encoding)
    elif compression_type == CompressionType.TAR_GZ:
        extractall_from_tar_gz(filepath, target_dir, file_names, password, encoding=encoding)
    elif compression_type == CompressionType.TAR_BZ2:
        extractall_from_tar_bz2(filepath, target_dir, file_names, password, encoding=encoding)
    elif compression_type == CompressionType.TAR_XZ:
        extractall_from_tar_xz(filepath, target_dir, file_names, password, encoding=encoding)
    else:
        raise ParameterValueError("Unknown extension")
