#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: _number.py
# @time: 2019/5/29 11:59
# @Software: PyCharm


__author__ = 'A.Star'

from astartool.common import hex_allowed_string, BIT_EACH
import numpy as np
from random import randint


def ishex(s: str):
    """
    判断一个字符串是否是16进制数
    :param s:
    :return:
    """
    for ch in s:
        if ch not in hex_allowed_string:
            return False
    return True


def gcd(a: int, b: int):
    """
    a和b的最大公约数
    :param a:
    :param b:
    :return:
    """
    while b != 0:
        a, b = b, a % b
    return a


def lcm(a: int, b: int):
    """
    a和b的最小公倍数
    :param a:
    :param b:
    :return:
    """
    return a // gcd(a, b) * b


def gcdlcm(a: int, b: int):
    """
    a和b的最大公约数和最小公倍数
    :param a:
    :param b:
    :return:
    """
    d = gcd(a, b)
    return d, a // d * b


def get_primes(number):
    """
    得到小于num的质数
    :param number:
    :return:
    """
    w = [True] * number
    li_number = []
    for i in range(2, number):
        if w[i]:
            w[i * i::i] = [False] * (len(range(i * i, number, i)))
            li_number.append(i)
    return li_number


def prime_factorization(number: int, li_number=None):
    """
    把一个数拆成其质因数之积
    :param number:
    :param li_number: 素数列表
    :return:
    """
    if li_number is None:
        li_number = get_primes(int(np.sqrt(number)) + 1)
    li = []
    for k in li_number:
        while not (number % k):
            li.append(k)
            number /= k
        if number == 1:
            break
    return li


def is_prime(number: (str, int), itor=10):
    """
    快速判断一个数是否为素数
    :param number:
    :param itor:
    :return:
    """
    if not isinstance(number, int):
        number = int(number)
    for i in range(itor):
        a = randint(1, number - 1)
        if pow(a, number - 1, number) != 1:
            return False
    return True


def rotate_left(a, k, mod=32):
    """
    a循环左移k位
    :param a:
    :param k:
    :param mod:
    :return:
    """
    k %= mod
    high, low = divmod(a, BIT_EACH[mod - k])
    return high + low * BIT_EACH[k]


def equals_zero(matrix, eps=1e-8):
    """
    判断每项是否是0
    :param matrix:
    :param eps:
    :return:
    """
    assert eps >= 0, "eps 应该大于0"
    if isinstance(matrix, np.ndarray):
        return (-eps < matrix) & (matrix < eps)
    if isinstance(matrix, list):
        return [-eps < each_x < eps for each_x in matrix]
    if isinstance(matrix, float):
        return -eps < matrix < eps
    raise ValueError('data must be ndarray or list')


def equals_zero_all(matrix, eps=1e-8):
    """
    判断是否是全0
    :param matrix:
    :param eps:
    :return:
    """
    return np.all(equals_zero(matrix, eps=eps))


def equals_zero_any(matrix, eps=1e-8):
    """
    判断是否是存在0
    :param matrix:
    :param eps:
    :return:
    """
    return np.any(equals_zero(matrix, eps=eps))
