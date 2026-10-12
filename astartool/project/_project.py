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


def _confirm_remove(file_path, show_text='remove file?\n[Y]yes\n[N]no\n'):
    """
    目标文件已存在时，通过 :func:`alert_dialog` 交互询问是否删除。

    只负责交互询问，不执行删除；删除动作与删除失败时的降级处理由调用方决定
    （如 :func:`_resolve_pdf_path` 需要在删除失败时降级为时间戳文件名）。

    :param file_path: 目标文件路径（str 或 pathlib.Path）
    :param show_text: 交互提示文本
    :return: 文件不存在、或用户确认删除返回 ``True``；用户拒绝删除返回 ``False``
    :rtype: bool
    """
    path = Path(file_path)
    if not path.exists():
        return True
    warnings.warn('file ' + str(path) + ' exist')
    confirmed = []

    def _mark_confirmed():
        confirmed.append(True)

    alert_dialog(okay_flag=lambda t: bool(t) and t[0] in ('Y', 'y'),
                 okay_callback=_mark_confirmed,
                 cancel_flag=None,
                 cancel_callback=None,
                 default_callback=None,
                 show_text=show_text,
                 okay_text='',
                 cancel_text='',
                 default_text='')
    return bool(confirmed)


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
    :param to_file: 目标文件路径（str 或 pathlib.Path）
    :param start_file: 文件头附加内容
    :param end_file: 文件尾附加内容
    :return: 写入的源码行数（不含 ``start_file`` / ``end_file`` 附加内容）；
        文件解码失败被跳过时返回 ``0``
    :rtype: int
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
                return 0
        outfile.write(str(src_path))
        outfile.write('\n')
        outfile.write(start_file)
        outfile.write(lines)
        outfile.write(end_file)
        return len(lines.splitlines())


def walk(root,
         to_file='out.txt',
         start_file='\n',
         end_file='\n',
         allow_extension=list_allow_extension,
         ignore=list_ignore):
    """
    递归遍历目录，将允许扩展名的文件内容拼接到目标文件（pathlib 版本）.

    :param root: 遍历根目录（str 或 pathlib.Path）
    :param to_file: 目标文件路径（str 或 pathlib.Path）
    :param start_file: 文件头附加内容
    :param end_file: 文件尾附加内容
    :param allow_extension: 需要转换的文件后缀集合
    :param ignore: 忽略的文件/文件夹名称或通配模式
    :return: 统计信息 ``{"file_count": 文件数, "source_lines": 源码总行数}``
    :rtype: dict
    """
    root_path = Path(root)
    stats = {'file_count': 0, 'source_lines': 0}
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
                source_lines = file_to_lines(src_file=child,
                                             to_file=to_file,
                                             start_file=start_file,
                                             end_file=end_file)
                stats['file_count'] += 1
                stats['source_lines'] += source_lines
        elif child.is_dir():
            sub_stats = walk(child,
                             to_file,
                             start_file,
                             end_file,
                             allow_extension,
                             ignore)
            stats['file_count'] += sub_stats['file_count']
            stats['source_lines'] += sub_stats['source_lines']
    return stats


def _compress_blank_lines_in_file(file_path, max_blank=1, encoding='utf-8'):
    """
    压缩文本文件中的连续空行（保留至多 ``max_blank`` 行），并去掉首尾空行。

    用于 :func:`project_to_lines` 导出后的后处理：源码拼接时每个文件头部与尾部
    都会附加空行（``start_file`` / ``end_file``），叠加源码自身的空行后文件中间
    会出现大量连续空行，软著排版时每页空白过多，故在此统一压缩。

    :param file_path: 目标文本文件路径（str 或 pathlib.Path）
    :param max_blank: 连续空行最多保留的行数，默认 1；设为 ``0`` 表示删除全部空行
    :param encoding: 文件编码
    :return:
    """
    path = Path(file_path)
    with path.open('r', encoding=encoding) as f:
        lines = f.read().splitlines()

    compressed = []
    blank_run = 0
    for line in lines:
        if line.strip() == '':
            blank_run += 1
            if blank_run <= max_blank:
                compressed.append(line)
        else:
            blank_run = 0
            compressed.append(line)
    while compressed and compressed[0].strip() == '':
        compressed.pop(0)
    while compressed and compressed[-1].strip() == '':
        compressed.pop()

    with path.open('w', encoding=encoding) as f:
        f.write('\n'.join(compressed))
        if compressed:
            f.write('\n')


def project_to_lines(src_project,
                     to_file='out.txt',
                     start_file='\n',
                     end_file='\n',
                     allow_extension=list_allow_extension,
                     ignore=list_ignore,
                     compress_blank=True,
                     max_blank=1):
    """
    项目打印为文件（申请软著用，pathlib 版本）.

    :param src_project: 源项目根目录（str 或 pathlib.Path）
    :param to_file: 转化到的文件名（str 或 pathlib.Path）
    :param start_file: 文件开始附加内容
    :param end_file: 文件结束附加内容
    :param allow_extension: 需要转换的文件后缀集合
    :param ignore: 忽略转换的文件和文件夹
    :param compress_blank: 是否压缩导出结果中的连续空行（保留至多
        ``max_blank`` 行）并去掉首尾空行，默认 ``True``；源码拼接时文件头尾附加
        空行叠加源码自身空行会导致中间空行过多，软著排版时需要处理
    :param max_blank: 连续空行最多保留的行数，默认 1；仅 ``compress_blank``
        为真时生效
    :return: 统计信息 ``{"file_count": 文件数, "source_lines": 源码总行数}``；
        源码总行数不含文件头尾附加内容，但含源码自身的空行与注释
    :rtype: dict
    """
    to_path = Path(to_file)
    if not _confirm_remove(to_path):
        # 用户选择保留已存在的目标文件，放弃本次导出
        return {'file_count': 0, 'source_lines': 0}
    if to_path.exists():
        to_path.unlink()
    stats = walk(src_project,
                 to_file,
                 start_file,
                 end_file,
                 allow_extension,
                 ignore)
    if compress_blank and to_path.exists():
        _compress_blank_lines_in_file(to_path, max_blank=max_blank)
    return stats


def _import_pdf_deps():
    """
    惰性导入 reportlab 相关组件。

    未安装 reportlab 时抛出带安装提示的 :class:`ImportError`，与其它可选依赖
    （openpyxl / xlwt / pillow）的处理方式保持一致。

    :return: ``(canvas 模块, pdfmetrics, UnicodeCIDFont, A4)``
    :rtype: tuple
    """
    try:
        from reportlab.pdfgen import canvas as canvas_module
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.lib.pagesizes import A4
    except ImportError:
        raise ImportError(
            "reportlab is required to export PDF. Install it via "
            "`pip install reportlab` or `pip install astartool[optional]`."
        )
    return canvas_module, pdfmetrics, UnicodeCIDFont, A4


def _paginate_lines(lines, lines_per_page):
    """
    把源码行列表按固定行数分页。

    :param lines: 源码行列表
    :param lines_per_page: 每页行数
    :return: 分页后的二维列表；空内容时返回一页空白页，保证 PDF 至少有 1 页
    :rtype: list
    """
    if not lines:
        return [[]]
    return [lines[i:i + lines_per_page]
            for i in range(0, len(lines), lines_per_page)]


def _resolve_pdf_path(pdf_path):
    """
    解析 PDF 输出路径，交互确认覆盖，并规避目标文件被占用导致写入失败。

    * 目标文件不存在：直接返回原路径；
    * 目标文件已存在：交互询问是否删除，拒绝则返回 ``None``（调用方放弃
      该 PDF 的导出）；
    * 确认删除但删除失败（文件被占用，如 PDF 阅读器打开中）：降级为带
      时间戳的文件名，保证导出不中断。

    :param pdf_path: 期望输出的 PDF 路径（str 或 pathlib.Path）
    :return: 实际可用的 PDF 路径；用户拒绝删除时为 ``None``
    :rtype: pathlib.Path or None
    """
    path = Path(pdf_path)
    if not _confirm_remove(path):
        return None
    if path.exists():
        try:
            path.unlink()
        except (PermissionError, OSError):
            stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            return path.with_name('%s_%s%s' % (path.stem, stamp, path.suffix))
    return path


def _render_source_pdf(pages, pdf_path, header, lines_per_page=50):
    """
    把分页后的源码行渲染为软著风格的源代码 PDF。

    排版规则：A4 纵向；页眉左侧为 ``header``（软件名+版本+源码总行数），右侧为
    页码；页眉下方与页脚上方各一条分隔线；正文每页固定行数，字号 8pt、行距
    12pt；单行超长截断，避免右侧溢出；无法用中文字体渲染的字符降级为 ``?``。

    :param pages: 分页后的二维源码行列表（:func:`_paginate_lines` 的返回值）
    :param pdf_path: 输出 PDF 路径（str 或 pathlib.Path）
    :param header: 页眉左侧文本
    :param lines_per_page: 每页行数（仅用于内部校验，分页已在外部完成）
    :return: PDF 总页数
    :rtype: int
    """
    canvas_module, pdfmetrics, UnicodeCIDFont, A4 = _import_pdf_deps()
    # STSong-Light 为 reportlab 内置中文 CID 字体，无需外部字体文件
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    font = 'STSong-Light'

    canvas = canvas_module.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    left = 30
    top = 56
    bottom = 50
    font_size = 8
    leading = 12
    max_cols = 120  # 单行截断宽度，避免右侧溢出

    total = len(pages)
    for idx, page_lines in enumerate(pages, start=1):
        canvas.setFont(font, 10)
        canvas.drawString(left, height - 36, header)
        canvas.setFont(font, 8)
        canvas.drawRightString(width - left, height - 36,
                               '第 %d 页 / 共 %d 页' % (idx, total))
        canvas.line(left, height - 42, width - left, height - 42)

        canvas.setFont(font, font_size)
        y = height - top
        for raw in page_lines:
            line = raw[:max_cols]
            try:
                canvas.drawString(left, y, line)
            except Exception:
                # 个别字符不在中文字体编码范围内时降级为 ASCII 占位
                safe = ''.join(ch if ord(ch) < 128 else '?' for ch in line)
                canvas.drawString(left, y, safe)
            y -= leading

        canvas.line(left, bottom - 6, width - left, bottom - 6)
        canvas.showPage()

    canvas.save()
    return total


def project_to_pdf(src_project,
                   to_dir='softcopyright',
                   software_name='',
                   version=(1, 0, 0, 'final', 0),
                   allow_extension=list_allow_extension,
                   ignore=list_ignore,
                   start_file='\n',
                   end_file='\n',
                   lines_per_page=50,
                   keep_pages=30,
                   max_pages=60,
                   compress_blank=True,
                   max_blank=1,
                   encoding='utf-8'):
    """
    导出软著用源代码 PDF（输入工程根目录，输出源码 PDF 与软著提交版 PDF）.

    流程：

    1. 若 ``<to_dir>/source_code.txt`` 已存在，交互询问是否删除，用户拒绝则
       放弃本次导出（返回的 ``pdf`` 为 ``None``）；
    2. 调用 :func:`project_to_lines` 把工程源码拼接为
       ``<to_dir>/source_code.txt``（自动压缩连续空行）；
    3. 排版为完整源码 PDF ``<to_dir>/source_code.pdf``（A4、每页固定行数、
       页眉含软件名+版本+源码总行数、页脚页码）；目标 PDF 已存在时同样
       交互询问是否删除，拒绝则放弃导出；
    4. 按软著要求：总页数超过 ``max_pages``（默认 60 页）时，只提交前
       ``keep_pages`` 页 + 后 ``keep_pages`` 页（默认各 30 页），另存为
       ``<to_dir>/source_code_head<N>_tail<N>.pdf``；未超过时无需拆分，
       ``pdf_part`` 为 ``None``（完整版即提交版）；提交版 PDF 已存在时
       同样交互询问，拒绝则仅输出完整版。

    依赖 reportlab（可选依赖，未安装时抛出带安装提示的
    :class:`ImportError`）。

    :param src_project: 源项目根目录（str 或 pathlib.Path）
    :param to_dir: 输出目录（默认 ``softcopyright``，str 或 pathlib.Path），
        不存在则自动创建
    :param software_name: 软著登记的软件名称（页眉展示）
    :param version: 软件版本号，元组（如 ``(1, 0, 0, 'final', 0)``）或字符串
    :param allow_extension: 需要转换的文件后缀集合
    :param ignore: 忽略转换的文件和文件夹
    :param start_file: 每个源码文件头部附加内容
    :param end_file: 每个源码文件尾部附加内容
    :param lines_per_page: PDF 每页行数，默认 50
    :param keep_pages: 软著提交版前后各自保留的页数，默认 30
    :param max_pages: 超过该页数才拆分软著提交版，默认 60
    :param compress_blank: 是否压缩拼接结果中的连续空行，默认 ``True``
    :param max_blank: 连续空行最多保留的行数，默认 1
    :param encoding: 文本文件编码
    :return: 统计信息字典，键含义：

        * ``txt``: 拼接出的源码文本路径
        * ``pdf``: 完整源码 PDF 路径；源码文本或完整版 PDF 已存在且用户
          拒绝删除、放弃本次导出时为 ``None``
        * ``pdf_part``: 软著提交版（前后各 ``keep_pages`` 页）PDF 路径；
          未超过 ``max_pages``、放弃导出、或用户拒绝删除已存在的提交版
          PDF 时为 ``None``
        * ``total_pages``: 完整源码 PDF 总页数（放弃导出时为 0）
        * ``part_pages``: 软著提交版页数（未拆分时等于 ``total_pages``，
          未生成时为 0）
        * ``source_lines``: 源码总行数（含空行/注释，不含文件头尾附加内容）
        * ``file_count``: 源码文件数
    :rtype: dict

    示例::

        from astartool.project import project_to_pdf

        info = project_to_pdf(
            src_project='/path/to/project',
            to_dir='softcopyright',
            software_name='My Software',
            version=(1, 0, 0, 'final', 0),
        )
        print(info['pdf'], info['pdf_part'], info['source_lines'])
    """
    if isinstance(version, (tuple, list)):
        version_str = get_version(version)
    else:
        version_str = str(version)

    out_dir = Path(to_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_txt = out_dir / 'source_code.txt'
    # 源码文本已存在时不静默删除，交互确认；用户拒绝时放弃本次导出
    if not _confirm_remove(out_txt):
        return {
            'txt': out_txt,
            'pdf': None,
            'pdf_part': None,
            'total_pages': 0,
            'part_pages': 0,
            'source_lines': 0,
            'file_count': 0,
        }
    if out_txt.exists():
        out_txt.unlink()

    stats = project_to_lines(
        src_project=src_project,
        to_file=str(out_txt),
        start_file=start_file,
        end_file=end_file,
        allow_extension=allow_extension,
        ignore=ignore,
        compress_blank=compress_blank,
        max_blank=max_blank,
    )

    with out_txt.open('r', encoding=encoding) as f:
        lines = f.read().splitlines()

    header = '%s  v%s  源代码（共 %d 行）' % (
        software_name, version_str, stats['source_lines'])
    pages = _paginate_lines(lines, lines_per_page)
    total_pages = len(pages)

    pdf_path = _resolve_pdf_path(out_dir / 'source_code.pdf')
    if pdf_path is None:
        # 用户拒绝删除已存在的完整版 PDF，放弃本次导出
        return {
            'txt': out_txt,
            'pdf': None,
            'pdf_part': None,
            'total_pages': 0,
            'part_pages': 0,
            'source_lines': stats['source_lines'],
            'file_count': stats['file_count'],
        }
    _render_source_pdf(pages, pdf_path, header, lines_per_page=lines_per_page)

    result = {
        'txt': out_txt,
        'pdf': pdf_path,
        'pdf_part': None,
        'total_pages': total_pages,
        'part_pages': total_pages,
        'source_lines': stats['source_lines'],
        'file_count': stats['file_count'],
    }

    if total_pages > max_pages:
        # 软著惯例：超过 max_pages 页只提交前 keep_pages 页 + 后 keep_pages 页
        part_pages = pages[:keep_pages] + pages[-keep_pages:]
        part_path = _resolve_pdf_path(
            out_dir / ('source_code_head%d_tail%d.pdf' % (keep_pages, keep_pages)))
        if part_path is None:
            # 用户拒绝删除已存在的软著提交版 PDF：仅保留完整版
            result['part_pages'] = 0
            return result
        _render_source_pdf(part_pages, part_path, header,
                           lines_per_page=lines_per_page)
        result['pdf_part'] = part_path
        result['part_pages'] = len(part_pages)

    return result
