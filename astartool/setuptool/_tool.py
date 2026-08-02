#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: _tool.py
# @time: 2019/5/29 11:27
# @Software: PyCharm


__author__ = 'A.Star'

import os
import sys
import pathlib

from setuptools import setup as _setup

from astartool.project import alert_dialog

osp = os.path


def load_install_requires(filepath='requirements.txt', encoding='utf-8'):
    """
    通过filepath生成setup.py的install_requires
    :param filepath:
    :param encoding:
    :return:
    """
    file = pathlib.Path(filepath)
    if file.exists():
        with file.open('r', encoding=encoding) as f:
            lines = f.readlines()
        requirements = (line.split('#')[0].strip() for line in lines if not line.strip().startswith('#') and not line.startswith('-'))
        return [req for req in requirements if requirements]
    else:
        raise FileNotFoundError("file not found")


def read_file(file_name='README.md', encoding='utf-8'):
    """
    读取本地文件
    :param file_name: 文件名
    :param encoding: 文件编码，默认utf-8
    :return:
    """
    return pathlib.Path(file_name).open('r', encoding=encoding).read()


def __dialog_setup():
    print("Version is not final, do you really wants to setup it?")
    print("[Y] yes.")
    print("[N] no.")


def setup(**attrs):
    # Accept both the legacy ``api`` key (a version tuple, used by older
    # callers) and the standard ``version`` key (string or tuple). The custom
    # "non-final version" confirmation only applies when an ``api`` tuple with
    # a status segment is supplied; otherwise we delegate straight to
    # setuptools so the standard build flow (pip install -e . / setup.py
    # develop) works without requiring the legacy ``api`` argument.
    version = attrs.get('api', attrs.get('version'))
    if isinstance(version, tuple) and len(version) > 3:
        if version[3] not in ['F', 'f', 'final', 'Final']:
            show_text = "Version is not final, do you really wants to setup it?\n[Y] yes.\n[N] no."
            ok_flag = lambda inp: inp[0] in ['Y', 'y']
            yes_callback = None
            no_callback = lambda: sys.exit()
            alert_dialog(ok_flag,
                         cancel_flag=True,
                         show_text=show_text,
                         okay_callback=yes_callback,
                         cancel_callback=no_callback)

    return _setup(**attrs)
