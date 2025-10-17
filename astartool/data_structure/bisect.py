# -*- coding: utf-8 -*-

import bisect as sys_bisect


def __bisect_right(a, x, lo, hi, func):
    while lo < hi:
        mid = (lo + hi) // 2
        if x < func(a[mid]):
            hi = mid
        else:
            lo = mid + 1
    return lo


def __bisect_left(a, x, lo, hi, func):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if func(a[mid]) < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def __insort_right(a, func_x, lo, hi, x, func):
    while lo < hi:
        mid = (lo + hi) // 2
        if func_x < func(a[mid]):
            hi = mid
        else:
            lo = mid + 1
    a.insert(lo, x)


def __insort_left(a, func_x, lo, hi, x, func):
    while lo < hi:
        mid = (lo + hi) // 2
        if func(a[mid]) < func_x:
            lo = mid + 1
        else:
            hi = mid
    a.insert(lo, x)


def bisect_right(a, x, lo=0, hi=None, func=None, key_do_func=True):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    if func is None:
        return sys_bisect.bisect(a, x, lo, hi)
    if key_do_func:
        return __bisect_right(a, func(x), lo, hi, func)
    else:
        return __bisect_right(a, x, lo, hi, func)


def bisect_left(a, x, lo=0, hi=None, func=None, key_do_func=True):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    if func is None:
        return sys_bisect.bisect_left(a, x, lo, hi)
    if key_do_func:
        return __bisect_left(a, func(x), lo, hi, func)
    else:
        return __bisect_left(a, x, lo, hi, func)


def insort_right(a, x, lo=0, hi=None, func=None):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    if func is None:
        return sys_bisect.insort_right(a, x, lo, hi)
    return __insort_right(a, func(x), lo, hi, x, func)


def insort_left(a, x, lo=0, hi=None, func=None):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    if func is None:
        return sys_bisect.insort_left(a, x, lo, hi)
    return __insort_left(a, func(x), lo, hi, x, func)


bisect = bisect_right
insort = insort_right
