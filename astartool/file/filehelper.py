#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: filehelper.py
# @time: 2024/9/2 17:33
# @Software: PyCharm


import os
from pysmx.crypto import hashlib

from astartool.project import is_windows
from astartool.file.compresshelper import namelist as compress_name_list
from astartool.error import ParameterValueError
from astartool.exception.file_exception import FileReleaseLockException


def CalcSha1(filepath):
    """
    计算文件SHA1
    :param filepath:
    :param encoding:
    :return:
    """
    with open(filepath, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        hash = sha1obj.hexdigest()
        return hash


def CalcMD5(filepath):
    """
    计算文件MD5
    :param filepath:
    :return:
    """
    with open(filepath, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash


def CalcSM3(filepath):
    with open(filepath, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash


alg_map = {
    "md5": CalcMD5,
    "sm3": CalcSM3,
    "sha1": CalcSha1
}


def CalcHash(filepath, algorithm='md5'):
    return alg_map[algorithm.lower()](filepath)


def file_extension(path):
    """
    文件扩展名
    :param path:
    :return:
    """
    return os.path.splitext(path)[1]


def namelist(filepath):
    """
    zip/rar/tar文件名列表
    :param filepath:
    :return:
    """
    try:
        return compress_name_list(filepath)
    except ParameterValueError as e:
        filepath, tempfilename = os.path.split(filepath)
        return [tempfilename]


def get_file_name(filepath):
    """
    通过文件路径获得文件名(无论路径是否真正存在对应的文件)
    :param filepath:
    :return:
    """
    strsplit = str(filepath).split('/')
    filename = strsplit[-1]
    return filename


def rename(filepath, method='sha1', encoding='utf-8'):
    """
    通过加sha的方式重新命名文件
    :param filepath:
    :return:
    """
    splitext = os.path.splitext(filepath)
    f = alg_map.get(method.lower(), CalcSha1)
    hash = f(filepath)
    new_name = method + '_' + str(splitext[0]) + '_' + hash + splitext[-1]
    return new_name


def is_file_using(file_name):
    """
    判断文件是否被占用（是否存在文件锁）
    :param file_name:
    :return:
    """
    if is_windows():
        try:
            import win32file
        except ImportError as e:
            raise ImportError("Package `win32file` is not found, you may run `pip install pywin32` in cmd console")

        vHandle = None
        try:
            vHandle = win32file.CreateFile(file_name, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, None)
            return int(vHandle) == win32file.INVALID_HANDLE_VALUE
        except:
            return True
        finally:
            try:
                if vHandle is not None:
                    win32file.CloseHandle(vHandle)
            except:
                pass
    else:
        import fcntl
        # 打开文件
        file_descriptor = os.open(file_name, os.O_WRONLY)
        # 获取文件锁的信息
        lock_data = fcntl.flock(file_descriptor, fcntl.F_GETLK)
        os.close(file_descriptor)
        return lock_data.l_type != fcntl.F_UNLCK


def release_lock(filepath, no_lock_exception=False):
    """
    解除文件锁定
    :param filepath: 文件路径
    :param no_lock_exception: True: 如果文件无锁/无占用，抛出异常; False: 如果文件无锁/无占用，不抛出异常
    """
    if not is_file_using(filepath):
        if no_lock_exception:
            raise FileReleaseLockException("No lock to remove on {filepath}".format(filepath=filepath))
        return
    if is_windows():
        try:
            import win32api
            import win32con
        except ImportError:
            raise ImportError("Package `win32api` or `win32con` is not found, you may run `pip install pywin32` in cmd console")
        try:
            win32api.CloseHandle(win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, win32api.GetCurrentProcess()))
        except Exception as e:
            raise FileReleaseLockException("Error removing file lock: {e}".format(e=e))
    else:
        import fcntl
        # 打开文件
        file_descriptor = None
        try:
            file_descriptor = os.open(filepath, os.O_WRONLY)
            fcntl.flock(file_descriptor, fcntl.F_UNLCK)
        except IOError as e:
            raise FileReleaseLockException("Error removing file lock: {e}".format(e=e))
        finally:
            if file_descriptor is not None:
                os.close(file_descriptor)


def release_and_delete_file(filepath):
    """
    解锁文件并删除文件
    :param filepath:
    :return:
    """
    try:
        # 尝试删除文件
        os.unlink(filepath)
    except PermissionError:
        # 如果文件被占用，尝试解锁并再次删除
        try:
            release_lock(filepath, no_lock_exception=False)
            os.unlink(filepath)
        except Exception as e:
            raise FileReleaseLockException("Can not unlink file {filepath}: {e}".format(filepath=filepath, e=e))
