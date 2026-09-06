#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site:
# @file: project2lines.py
# @time: 2018/8/1 15:49
# @Software: PyCharm

import warnings
from pathlib import Path

from astartool.common import list_allow_extension, list_ignore
import re


def file_to_lines(src_file,
                  to_file='out.txt',
                  start_file='\n',
                  end_file='\n'):
    """
    文件打印到字符串中（pathlib 版本）.

    :param src_file: 源文件路径（str 或 pathlib.Path）
    :param to_file: 目标文件路径
    :param start_file: 文件头附加内容
    :param end_file: 文件尾附加内容
    :return:
    """
    src_path = Path(src_file)
    to_path = Path(to_file)
    with to_path.open('a+', encoding='utf-8') as outfile:
        raw = src_path.read_bytes()
        try:
            lines = raw.decode('gbk')
        except UnicodeError:
            try:
                lines = raw.decode('utf-8')
            except UnicodeError:
                return
        outfile.write(str(src_path))
        outfile.write('\n')
        outfile.write(start_file)
        outfile.write(lines)
        outfile.write(end_file)


def walk(root,
         to_file='out.txt',
         start_file='\n',
         end_file='\n',
         allow_extension=list_allow_extension,
         ignore=list_ignore):
    """
    递归遍历目录，将允许扩展名的文件内容拼接到目标文件（pathlib 版本）.

    :param root: 遍历根目录
    :param to_file: 目标文件路径
    :param start_file: 文件头附加内容
    :param end_file: 文件尾附加内容
    :param allow_extension: 需要转换的文件后缀集合
    :param ignore: 忽略的文件/文件夹名称或通配模式
    :return:
    """
    root_path = Path(root)
    for child in root_path.iterdir():
        flag = True
        for each in ignore:
            if '*' in each:
                try:
                    if re.findall(each, child.name):
                        flag = False
                        break
                except re.error:
                    pass
            else:
                if child.name == each or (child.name == each[:-1] and each.endswith('/')):
                    flag = False
                    break
        if not flag:
            continue
        if child.is_file():
            if child.suffix in allow_extension and str(child) not in ignore:
                file_to_lines(src_file=child,
                              to_file=to_file,
                              start_file=start_file,
                              end_file=end_file)
        elif child.is_dir():
            walk(child,
                 to_file,
                 start_file,
                 end_file,
                 allow_extension,
                 ignore)


def project_to_lines(src_project,
                     to_file='out.txt',
                     start_file='\n',
                     end_file='\n',
                     allow_extension=list_allow_extension,
                     ignore=list_ignore):
    """
    项目打印为文件（申请软著用，pathlib 版本）.

    :param src_project: 源项目根目录
    :param to_file: 转化到的文件名
    :param start_file: 文件开始附加内容
    :param end_file: 文件结束附加内容
    :param allow_extension: 需要转换的文件后缀集合
    :param ignore: 忽略转换的文件和文件夹
    :return:
    """
    to_path = Path(to_file)
    if to_path.exists():
        warnings.warn('file ' + str(to_path) + ' exist')
        txt = input('remove file?\n[Y]yes\n[N]no\n')
        if txt and txt[0] in ('Y', 'y'):
            to_path.unlink()
        else:
            return
    walk(src_project,
         to_file,
         start_file,
         end_file,
         allow_extension,
         ignore)


if __name__ == '__main__':
    project_to_lines(src_project='',
                     # start_file='\n' + '-' * 15 + '\n',
                     # end_file='\n' + '-' * 15 + '\n\n'
                     allow_extension=['.py',
                                      '.jl',
                                      '.m',
                                      '.js',
                                      '.java',
                                      '.xml',
                                      '.html',
                                      '.htm',
                                      '.css',
                                      '.cs',
                                      '.cpp',
                                      '.c',
                                      '.h',
                                      '.php'],
                     ignore=[])
