#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 深圳星河软通科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.astar.ltd
# @file: _decorators.py
# @time: 2019/11/13 16:26
# @Software: PyCharm


import wrapt
import logging
import importlib
import warnings
from astartool.common import LOG_LEVEL_MAP_INT2STR, LOG_LEVEL_MAP_STR2INT, LOG_LEVEL_STR, LOG_LEVEL_INT


class VersionDeprecatedError(RuntimeError):
    """
    Raised when a decorated callable is invoked on a version above the
    deprecation transition interval, i.e. the method is no longer usable.
    """


def _parse_version(version):
    """
    Normalize a version into a comparable tuple.

    :param version: a version tuple (e.g. ``(0, 3, 0)``) or string
        (e.g. ``"0.3.0"``); strings are converted via
        :func:`astartool.setuptool._version.get_version_tuple`
    :return: comparable version tuple
    :rtype: tuple
    """
    if isinstance(version, str):
        from astartool.setuptool._version import get_version_tuple
        return get_version_tuple(version)
    if isinstance(version, (tuple, list)):
        return tuple(version)
    return version


def _resolve_transition(deprecated_since, removed_in):
    """
    Resolve the deprecation interval into ``(low, high)`` comparable tuples.

    :param deprecated_since: deprecation start version (interval lower bound)
    :param removed_in: removal version (interval upper bound, exclusive)
    :return: ``(low, high)`` version tuples
    :rtype: tuple
    """
    low = _parse_version(deprecated_since)
    high = _parse_version(removed_in) if removed_in is not None else low
    return low, high


def deprecated_version(deprecated_since, removed_in=None, current_version=None,
                      message=None, removed_message=None,
                      exception=VersionDeprecatedError):
    """
    惰性版本过期提示装饰器。

    在首次调用被装饰函数时，将当前版本号与过渡区间 ``[deprecated_since, removed_in)``
    对比：

    * 当前版本 **低于** ``deprecated_since``：未进入弃用期，正常执行，无提示；
    * 当前版本 **处于** 区间内（``deprecated_since <= current < removed_in``）：
      发出弃用 ``DeprecationWarning`` 提示切换方法，但函数**仍可使用**；
    * 当前版本 **达到/高于** ``removed_in``（``current >= removed_in``）：发出弃用
      提示，并抛出异常，函数**不再可用**。

    当前版本默认取自 ``astartool.version``；若传入字符串则自动转为元组比较。

    :param deprecated_since: 弃用起始版本（过渡区间下界），可为元组或字符串
    :param removed_in: 移除版本（过渡区间上界，开区间）；为 ``None`` 时取
        ``deprecated_since``，即该版本起既提示又不可用
    :param current_version: 当前版本；为 ``None`` 时取 ``astartool.version``；
        可为元组或字符串
    :param message: 区间内（弃用但仍可用）的自定义提示，支持 ``{current}`` /
        ``{transition}`` / ``{func}`` 占位符；为 ``None`` 用默认文案
    :param removed_message: 已达移除版本（不可用）的自定义提示，占位符同上；
        为 ``None`` 时复用 ``message`` 并追加不可用说明
    :param exception: 版本达到移除界限时抛出的异常类（默认
        :class:`VersionDeprecatedError`）
    :return: 装饰器

    示例::

        @deprecated_version((0, 3, 0), (0, 4, 0),
                            message="old_api 已弃用，请改用 new_api")
        def old_api():
            return "legacy"
    """
    _marker = object()

    def decorator(wrapped):
        # 缓存区间判断结果；_marker=尚未判断
        wrapped.__deprecation_state__ = _marker

        @wrapt.decorator
        def wrapper(wrapped_inner, instance, args, kwargs):
            state = wrapped_inner.__deprecation_state__
            if state is _marker:
                low, high = _resolve_transition(deprecated_since, removed_in)
                if current_version is None:
                    from astartool import version as _ver
                    current = _parse_version(_ver)
                else:
                    current = _parse_version(current_version)
                if current >= high:
                    state = "removed"
                elif current >= low:
                    state = "deprecated"
                else:
                    state = "active"
                wrapped_inner.__deprecation_state__ = state
                wrapped_inner.__deprecation_low__ = low
                wrapped_inner.__deprecation_high__ = high
                wrapped_inner.__deprecation_current__ = current

            if state == "active":
                return wrapped_inner(*args, **kwargs)

            ctx = {
                "current": wrapped_inner.__deprecation_current__,
                "transition": wrapped_inner.__deprecation_high__,
                "func": wrapped_inner.__name__,
            }
            if state == "deprecated":
                if message is None:
                    warn_msg = ("{func}() is deprecated since version "
                                "{transition} (current: {current}). It still "
                                "works but will be removed; please switch to "
                                "the recommended API.").format(**ctx)
                else:
                    warn_msg = message.format(**ctx)
                warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
                return wrapped_inner(*args, **kwargs)
            else:  # removed
                if removed_message is None:
                    if message is None:
                        err_msg = ("{func}() has been removed since version "
                                   "{transition} (current: {current}). This "
                                   "method is no longer available; please "
                                   "switch to the recommended API.").format(**ctx)
                    else:
                        err_msg = message.format(**ctx) + (" (current: {current}, "
                                                           "removed since {transition})").format(**ctx)
                else:
                    err_msg = removed_message.format(**ctx)
                raise exception(err_msg)

        return wrapper(wrapped)

    return decorator


def require_optional_import(module_name, error_message=None, exception=ImportError):
    """
    惰性加载装饰器：在被装饰函数首次调用时尝试导入 ``module_name``。

    若导入成功则正常执行函数；若导入失败（``ModuleNotFoundError`` / ``ImportError``）
    则抛出定制异常，异常信息可通过 ``error_message`` 自定义。

    :param module_name: 需要惰性导入的包/模块名（如 ``"numpy"``、``"openpyxl"``）
    :param error_message: 自定义报错信息；可包含 ``"{module}"`` 占位符，运行时替换为
        ``module_name``；为 ``None`` 时使用默认提示
    :param exception: 导入失败时抛出的异常类（默认 ``ImportError``）
    :return: 装饰器

    示例::

        @require_optional_import("numpy", "请先安装 numpy: pip install numpy")
        def heavy_compute():
            import numpy as np
            return np.array([1, 2, 3])
    """
    _marker = object()

    def decorator(wrapped):
        # 缓存导入探测结果：True=可用, False=不可用, _marker=尚未探测
        wrapped.__optional_import_ok__ = _marker

        @wrapt.decorator
        def wrapper(wrapped_inner, instance, args, kwargs):
            state = wrapped_inner.__optional_import_ok__
            if state is _marker:
                try:
                    importlib.import_module(module_name)
                    wrapped_inner.__optional_import_ok__ = True
                except ImportError:
                    wrapped_inner.__optional_import_ok__ = False
            if wrapped_inner.__optional_import_ok__ is False:
                if error_message is None:
                    msg = ("Optional dependency '{module}' is required by "
                           "{func}() but is not installed. Install it to use "
                           "this feature.").format(module=module_name,
                                                   func=wrapped_inner.__name__)
                else:
                    msg = error_message.format(module=module_name)
                raise exception(msg)
            return wrapped_inner(*args, **kwargs)

        return wrapper(wrapped)

    return decorator


def std_logging(level=logging.INFO):
    """
    日志记录
    :param level:
    :return:
    """
    int_flag = level in LOG_LEVEL_INT
    assert int_flag or level in LOG_LEVEL_STR
    if int_flag:
        level = LOG_LEVEL_MAP_INT2STR[level]

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        print("[{}]: enter {}()".format(level, wrapped.__name__))
        f = wrapped(*args, **kwargs)
        print("[{}]: exit {}()".format(level, wrapped.__name__))
        return f

    return wrapper


def file_logging(level=logging.INFO):
    """
    日志记录
    :param level:
    :return:
    """
    str_flag = level in LOG_LEVEL_STR
    assert str_flag or level in LOG_LEVEL_INT
    if str_flag:
        level = LOG_LEVEL_MAP_STR2INT[level]

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        logging.log(level, "enter {}()".format(wrapped.__name__))
        f = wrapped(*args, **kwargs)
        logging.log(level, "exit {}()".format(wrapped.__name__))
        return f

    return wrapper
