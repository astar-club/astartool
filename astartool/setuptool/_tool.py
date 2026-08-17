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


def load_install_requires(filepath='requirements.txt', encoding='utf-8', extra=None):
    """
    通过filepath生成setup.py的install_requires

    :param filepath: requirements 文件路径
    :param encoding: 文件编码
    :param extra: 可选依赖分组名（如 ``"optional"``）；为 ``None`` 时读取主段，
        遇到 ``[section]`` 标题后停止（除非 section 与 extra 匹配）
    :return: 依赖列表
    :rtype: list
    """
    file = pathlib.Path(filepath)
    if not file.exists():
        raise FileNotFoundError("file not found")
    with file.open('r', encoding=encoding) as f:
        lines = f.readlines()

    target = extra  # None 表示读取主段
    requirements = []
    in_target = (target is None)
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('[') and stripped.endswith(']'):
            section = stripped[1:-1].strip()
            in_target = (section == target)
            continue
        if not in_target:
            continue
        if stripped.startswith('#') or stripped.startswith('-'):
            continue
        req = stripped.split('#')[0].strip()
        if req:
            requirements.append(req)
    return requirements


def read_file(file_name='README.md', encoding='utf-8'):
    """
    读取本地文件

    委托给 :func:`astartool.file.file_opt.read_file` 以保证两者返回一致
    （默认参数下即整文件读取，返回与 ``Path.read_text()`` 相同的字符串）。

    :param file_name: 文件名
    :param encoding: 文件编码，默认utf-8
    :return: 文件文本内容
    :rtype: str
    """
    from astartool.file.file_opt import read_file as _read_file
    return _read_file(file_path=file_name, encoding=encoding)


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
