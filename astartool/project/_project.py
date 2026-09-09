#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: _project.py
# @time: 2019/6/8 11:53
# @Software: PyCharm


__author__ = 'A.Star'

import datetime
import logging
import os
import re
import sys
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Tuple

from astartool.data_structure.keymap import KeyMap
from astartool.common import list_allow_extension, list_ignore, item_field, item_foreignkey
from astartool.setuptool import get_version

type_disp_mapper = KeyMap({
    'IntegerField': '整型',
    'DateTimeField': '时间类型',
    'CharField': '变长字符串',
    'EmailField': '邮箱类型'
})

field_disp_mapper = KeyMap({
    'type': '类型',
    'verbose_name': '名称',
    'max_length': '最大长度',
    'model': '模型',
    'auto_created': '是否自动生成',
    'auto_now': '是否自动更新',
    'on_delete': '删除',
    'blank': '可否为空格',
    'null': '可否为空',
    'unique': '是否唯一'
})


def alert_dialog(okay_flag,
                 okay_callback=None,
                 cancel_flag: (callable, bool) = lambda x: False,
                 cancel_callback=None,
                 default_callback=None,
                 show_text=None,
                 okay_text='okay',
                 cancel_text='cancel',
                 default_text='default',
                 *args, **kwargs):
    res = None
    txt = input(show_text)
    if okay_flag is not None and okay_flag(txt):
        if okay_callback is not None:
            res = okay_callback(*args, **kwargs)
        print(okay_text)
        return res
    elif cancel_flag is not None and cancel_flag(txt):
        if cancel_callback is not None:
            res = cancel_callback(*args, **kwargs)
        print(cancel_text)
        return res
    else:
        if default_callback is not None:
            res = default_callback(*args, **kwargs)
        print(default_text)
        return res


def check_exist(to_file):
    if os.path.exists(to_file):
        warnings.warn('file ' + to_file + ' exist')
        okay_callback = lambda: os.remove(to_file)
        default_callback = lambda: sys.exit()
        txt = 'remove file?\n[Y]yes\n[N]no\n'
        okay_flag = lambda t: t[0] == 'Y' or t[0] == 'y'

        alert_dialog(okay_flag,
                     okay_callback,
                     cancel_flag=None,
                     cancel_callback=None,
                     default_callback=default_callback,
                     show_text=txt,
                     okay_text='',
                     cancel_text='',
                     default_text='')


def file_to_lines(src_file,
                  to_file='out.txt',
                  start_file='\n',
                  end_file='\n'):
    """
    文件打印到字符串中
    :param src_file: 源文件
    :param to_file: 目标文件
    :param start_file: 文件头
    :param end_file: 文件尾
    :return:
    """
    with open(to_file, 'a+', encoding='utf-8') as outfile, open(src_file, 'rb') as infile:
        bytes_lines = infile.readlines()
        try:
            lines = [each_line.decode('gbk') for each_line in bytes_lines]
        except UnicodeDecodeError as e:
            # print(e)
            try:
                lines = [each_line.decode('utf8') for each_line in bytes_lines]
            except UnicodeDecodeError as e:
                # print(e)
                logging.error("encode exception")
                return
                # lines = [each_line.decode('unicode') for each_line in lines]
        outfile.write(src_file)
        outfile.write('\n')
        outfile.write(start_file)
        outfile.writelines(lines)
        outfile.write(end_file)


def walk(root,
         to_file='out.txt',
         start_file='\n',
         end_file='\n',
         allow_extension=list_allow_extension,
         ignore=list_ignore):
    for i in os.listdir(root):
        flag = True
        for each in ignore:
            if '*' in each:
                try:
                    if re.findall(each, i):
                        flag = False
                        break
                except:
                    pass
            else:
                if i == each or (i == each[:-1] and each.endswith('/')):
                    flag = False
                    break
        if flag:
            src_file = os.path.join(root, i)
            if os.path.isfile(src_file):
                if os.path.splitext(src_file)[1] in allow_extension and src_file not in ignore:
                    file_to_lines(src_file=src_file,
                                  to_file=to_file,
                                  start_file=start_file,
                                  end_file=end_file
                                  )
            else:
                walk(src_file, to_file, start_file, end_file, allow_extension, ignore)


def project_to_lines(src_project,
                     to_file='out.txt',
                     start_file='\n',
                     end_file='\n',
                     allow_extension=list_allow_extension,
                     ignore=list_ignore):
    """
    项目打印为文件（申请软著用）
    :param src_project: 源文件项目根目录
    :param to_file: 转化到的文件名
    :param start_file: 文件开始
    :param end_file: 文件结束
    :param allow_extension: 需要转换的文件后缀
    :param ignore: 忽略转换的文件和文件夹
    :return:
    """
    check_exist(to_file)
    walk(src_project, to_file, start_file, end_file, allow_extension, ignore)


def auto_title_md(to_file: str,
                  version: Tuple[tuple, str] = (0, 1, 0, 'final', 0),
                  datetime=datetime.datetime.now(),
                  title='自动生成数据库模板头',
                  auth='ASTARTOOL ROBOT',
                  *,
                  encoding='utf-8'):
    """
    生成导出文件的模板头
    :param to_file: 导出文件名， 必填
    :param version: 版本号，tuple或者string
    :param datetime: 生成日期
    :param title: 标题
    :param auth: 作者
    :param encoding: 编码方式
    :return:
    """
    assert to_file is not None, "输出文件参数不能为空"
    if isinstance(version, tuple):
        version = get_version(version)
    check_exist(to_file)
    with open(to_file, 'w', encoding=encoding) as f:
        f.write("# " + title + '\n\n')
        f.write("**Version: {}**\n".format(version))
        f.write("**Auth:    {}**\n".format(auth))
        f.write("**Date:    {}**\n".format(datetime))

        f.write('\n\n')


def auto_title_rst(to_file: str,
                   version: (tuple, str) = (0, 1, 0, 'final', 0),
                   datetime=datetime.datetime.now(),
                   title='自动生成数据库模板头',
                   auth='ASTARTOOL ROBOT',
                   *, encoding='utf-8'):
    """
    生成导出文件的模板头
    :param to_file: 导出文件名， 必填
    :param version: 版本号，tuple或者string
    :param datetime: 生成日期
    :param title: 标题
    :param auth: 作者
    :param encoding: 编码方式
    :return:
    """
    assert to_file is not None, "输出文件参数不能为空"
    if isinstance(version, tuple):
        version = get_version(version)
    check_exist(to_file)
    with open(to_file, 'w', encoding=encoding) as f:
        f.write(title + '\n')
        f.write('==' * len(title))
        f.write('\n\n')
        f.write("**Version: {}**\n".format(version))
        f.write("**Auth:    {}**\n".format(auth))
        f.write("**Date:    {}**\n".format(datetime))
        f.write('\n\n')


def auto_title(to_file: str,
               version: Tuple[tuple, str] = (0, 1, 0, 'final', 0),
               datetime=datetime.datetime.now(),
               title='自动生成数据库模板头',
               auth='ASTARTOOL ROBOT',
               *, encoding='utf-8',
               doc_type='md'):
    """
    生成导出文件的模板头
    :param to_file: 导出文件名， 必填
    :param version: 版本号，tuple或者string
    :param datetime: 生成日期
    :param title: 标题
    :param auth: 作者
    :param encoding: 编码方式
    :param doc_type: 文档方式，默认为markdown, 同时支持rst
    :return:
    """
    if doc_type.lower() in ('md', 'markdown'):
        auto_title_md(to_file=to_file,
                      version=version,
                      datetime=datetime,
                      title=title,
                      auth=auth,
                      encoding=encoding)
    else:
        auto_title_rst(to_file=to_file,
                       version=version,
                       datetime=datetime,
                       title=title,
                       auth=auth,
                       encoding=encoding)


def model_to_dict(model_path, encoding='utf-8'):
    """
    数据库模型文件导出成dict（基于文件处理）
    :param model_path:
    :param encoding:
    :return:
    """
    # 读取模型文件
    with open(model_path, 'r', encoding=encoding) as f:
        lines = f.readlines()
    class_name = ''
    dictionary = OrderedDict({})  # 待返回的结果
    item = OrderedDict({})  # 待处理的字典
    # 分行处理
    for line in lines:
        if line.startswith('#'):
            # 过滤掉注释
            pass
        elif line.startswith('class'):
            # 处理类名
            name = line.split(' ')[1].split('(')[0]
            class_name = name
            dictionary[name] = {}
            item = {}
        elif line.startswith('  ') or line.startswith('\t'):
            if line.startswith('        verbose_name ='):
                if '_meta' in item:
                    item['_meta'].update(dict(verbose_name=line.split('=')[-1].lstrip()))
                else:
                    item['_meta'] = dict(verbose_name=line.split('=')[-1].lstrip())
                continue
            if line.startswith('        verbose_name_plural ='):
                if '_meta' in item:
                    item['_meta'].update(dict(verbose_name_plural=line.split('=')[-1].lstrip()))
                else:
                    item['_meta'] = dict(verbose_name_plural=line.split('=')[-1].lstrip())
                continue
            # 处理字段名
            col = line.split('=', 1)
            if len(col) >= 2:
                name = col[0].strip()
                item[name] = {}
                value = col[1].strip().split('(')
                type_name = value[0]
                try:
                    fields_string = value[1].split(')')[0]
                except:
                    fields_string = col[1].strip()
                fields_item = fields_string.split(',')
                item[name]['type'] = type_name.split('.')[-1]
                if item[name]['type'] != 'ForeignKey':
                    for i, each in enumerate(fields_item):
                        c = each.split('=')
                        if len(c) == 2:
                            item[name][c[0].strip()] = c[1].strip()
                        else:
                            item[name][item_field[i]] = c[0].strip()
                else:
                    # 处理字段属性
                    for i, each in enumerate(fields_item):
                        each = each.strip()
                        if each == '':
                            continue
                        c = each.split('=')
                        if len(c) == 2:
                            item[name][c[0].strip()] = c[1].strip()
                        else:
                            item[name][item_foreignkey[i]] = c[0].strip()
            else:
                pass
        else:
            if class_name == '':
                continue
            dictionary[class_name] = dict(dictionary[class_name], **item)
            item = OrderedDict({})
    if item is not None and item is not {}:
        dictionary[class_name] = dict(dictionary[class_name], **item)
    return dictionary


def model_to_doc(model_path, to_file=None,
                 version: Tuple[tuple, str] = (0, 0, 1, 'final', 0),
                 datetime=datetime.datetime.now(),
                 title='自动生成数据库模板头',
                 auth='ASTARTOOL ROBOT',
                 *, encoding='utf-8'):
    """
    数据库model.py导出成文件
    :param model_path:
    :param to_file:
    :param version:
    :param datetime:
    :param title:
    :param auth:
    :param encoding:
    :return:
    """
    if isinstance(version, tuple):
        version = get_version(version)
    if to_file is None:
        to_file = 'database_model(auto v{}).md'.format(version)

    # 自动模板头
    auto_title(to_file, version=version, datetime=datetime,
               title=title, auth=auth, encoding=encoding)
    model_dict = model_to_dict(model_path, encoding=encoding)

    with open(to_file, 'a+', encoding=encoding) as f:
        for no, (each_class_key, each_class_values) in enumerate(model_dict.items()):
            f.write(str(no) + '. ' + each_class_key + '\n\n')
            f.write('|字段|字段描述|字段类型|字段信息|\n')
            f.write('|:--:|:--:|:--:|:--:|\n')
            for item_key, item_values in each_class_values.items():
                if item_key == '_meta':
                    continue
                verbose_name = item_values.pop('verbose_name', item_key)
                item_type = item_values.pop('type', verbose_name)
                item_info = [field_disp_mapper.get(k, k) + ':' + str(v) for k, v in item_values.items()]
                f.write('|'.join(
                    [item_key, verbose_name, type_disp_mapper.get(item_type, item_type), ','.join(item_info)]) + '\n')
            f.write('\n')


def url_to_interface_template(url_path, to_file=None,
                              version: Tuple[tuple, str] = (0, 0, 1, 'final', 0),
                              datetime=datetime.datetime.now(),
                              title='自动生成interface模板头',
                              auth='ASTARTOOL ROBOT',
                              *, encoding='utf-8'):
    """
    基于django的文件生成接口模板
    :param url_path:
    :param to_file:
    :param version:
    :param datetime:
    :param title:
    :param auth:
    :param encoding:
    :return:
    """
    if isinstance(version, tuple):
        version = get_version(version)
    if to_file is None:
        to_file = 'interface(auto v{}).md'.format(version)
    # 自动模板头
    auto_title(to_file, version=version, datetime=datetime,
               title=title, auth=auth, encoding=encoding)

    with open(url_path, 'r', encoding=encoding) as f:
        fs = f.read()

    context = fs.split("[")[1].split("]")[0]

    p = re.compile('[url|path]\((.*)\)')
    urls_pattern = re.findall(p, context)
    urls = []
    for each in urls_pattern:
        item = each.split('"')
        if len(item) == 1:
            item = each.split("'")
        urls.append(item[1])

    with open(to_file, 'a', encoding=encoding) as f:
        for ind, each in enumerate(urls):
            f.write(
                "- {1}\n\n|||||\n|:--:|:--:|:--:|:--:|\n|名称||||\n|分类|无|||\n|method||||\n|参数||||\n|||||\n|返回||||\n|||||\n\n".format(
                    ind, each))


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
