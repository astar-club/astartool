#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: setup.py
# @time: 2018/9/8 1:31
# @Software: PyCharm


import os
import re
import pathlib
import subprocess
import datetime
import functools
from setuptools import find_packages, setup as _setup

osp = os.path


def _read_version_tuple():
    """Read the `version` tuple from astartool/__init__.py without importing
    the package (importing would trigger `import wrapt` before install)."""
    init_path = osp.join(osp.dirname(__file__), 'astartool', '__init__.py')
    with open(init_path, encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'^version\s*=\s*\(([^)]*)\)', content, re.MULTILINE)
    if not m:
        raise RuntimeError('Could not find version tuple in astartool/__init__.py')
    return eval('({},)'.format(m.group(1)))


def load_install_requires(filepath='requirements.txt', encoding='utf-8', extra=None):
    """Parse requirements.txt into a list of install_requires.

    Mirrors astartool.setuptool.load_install_requires but does NOT import
    the package (which would pull in `wrapt` before it is installed).
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
    with open(file_name, 'r', encoding=encoding) as f:
        return f.read()


@functools.lru_cache()
def _get_git_changeset():
    repo_dir = osp.dirname(osp.abspath(__file__))
    git_log = subprocess.Popen(
        'git log --pretty=format:%ct --quiet -1 HEAD',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=repo_dir, universal_newlines=True,
    )
    timestamp = git_log.communicate()[0]
    try:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
    except ValueError:
        return None
    return timestamp.strftime('%Y%m%d%H%M%S')


def get_version(version):
    """Return a PEP 440-compliant version string from a version tuple.

    Mirrors astartool.setuptool.get_version but does NOT import the package.
    """
    length = len(version)
    assert length <= 5
    li = [0, 0, 0, 'final', 0]
    if length >= 3 and isinstance(version[2], str):
        li[:2] = version[:2]
        li[3:] = version[2:]
    else:
        li[:len(version)] = version
    version = tuple(li)
    assert version[3] in ('alpha', 'beta', 'rc', 'final', 'post', 'dev')

    main_parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:main_parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        git_changeset = _get_git_changeset()
        if git_changeset:
            sub = '.dev%s' % git_changeset
    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc', 'post': 'post', 'dev': 'dev'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


def setup(**attrs):
    # Accept both the legacy ``api`` key (a version tuple, used by older
    # callers) and the standard ``version`` key (string or tuple). The custom
    # "non-final version" confirmation only applies when an ``api`` tuple with
    # a status segment is supplied; otherwise delegate to setuptools.
    version = attrs.get('api', attrs.get('version'))
    if isinstance(version, tuple) and len(version) > 3:
        if version[3] not in ['F', 'f', 'final', 'Final']:
            show_text = "Version is not final, do you really wants to setup it?\n[Y] yes.\n[N] no."
            print(show_text)
            ok_flag = lambda inp: inp[0] in ['Y', 'y']
            if not ok_flag(input().strip()):
                raise SystemExit(1)

    return _setup(**attrs)


version = _read_version_tuple()

setup(
    name='astartool',
    version=get_version(version),
    description=(
        'astartool: a lightweight Python toolkit for data structures, file '
        'processing, and number/string utilities'
    ),
    long_description=read_file('README.md', encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='A.Star',
    author_email='astar@snowland.ltd',
    maintainer='A.Star',
    maintainer_email='astar@snowland.ltd',
    license='Apache v2.0',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/astar-club/astartool',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=load_install_requires(),
    extras_require={
        'optional': load_install_requires(extra='optional'),
    }
)
