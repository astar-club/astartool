#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: password_check .py
# @time: 2020/6/21 1:57
# @Software: PyCharm

import re


def check_length(pwd, min_length=8):
    """
    判断密码长度是否合法
    :param pwd:
    :param min_length:
    :return:
    """
    if isinstance(pwd, (str, bytes, bytearray)):
        return len(pwd) >= min_length
    else:
        return 0


def check_contain_upper(pwd):
    """
    判断是否包含大写字母
    :param pwd:
    :return:
    """
    if isinstance(pwd, (str, bytes, bytearray)):
        pattern = re.compile('[A-Z]+')
        match = pattern.findall(pwd)
        return len(match) != 0
    else:
        return False


def check_contain_num(pwd):
    """
    判断是或否包含数字
    :param pwd:
    :return:
    """
    if isinstance(pwd, (str, bytes, bytearray)):
        pattern = re.compile('[0-9]+')
        match = pattern.findall(pwd)
        return len(match) != 0
    else:
        return False


def check_contain_lower(pwd):
    """
    判断是或否包含小写字母
    :param pwd:
    :return:
    """
    if isinstance(pwd, (str, bytes, bytearray)):
        pattern = re.compile('[a-z]+')
        match = pattern.findall(pwd)
        return len(match) != 0
    else:
        return False


def check_symbol(pwd):
    """
    判断是或否包含特殊字符
    :param pwd:
    :return:
    """
    if isinstance(pwd, (str, bytes, bytearray)):
        pattern = re.compile('([^a-z0-9A-Z])+')
        match = pattern.findall(pwd)
        return len(match) != 0
    else:
        return False


def check_password(pwd, min_length=8, *, symbol=True):
    """
    判断密码是否合法
    :param pwd:
    :return:
    """
    # 判断密码长度是否合法
    lenOK = check_length(pwd, min_length)
    # 判断是否包含大写字母
    upperOK = check_contain_upper(pwd)
    # 判断是否包含小写字母
    lowerOK = check_contain_lower(pwd)
    # 判断是否包含数字
    numOK = check_contain_num(pwd)

    # 判断是否包含符号
    symbolOK = (not symbol) or check_symbol(pwd)
    return lenOK and upperOK and lowerOK and numOK and symbolOK
