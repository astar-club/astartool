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
import string
import inspect
from astartool.common import LOG_LEVEL_MAP_INT2STR, LOG_LEVEL_MAP_STR2INT, LOG_LEVEL_STR, LOG_LEVEL_INT




def _bind_arguments(wrapped, args, kwargs):
    """
    将实参绑定到被装饰函数的形参，返回有序字典 ``{形参名: 实参值}``。

    例如 ``foo(x, y)`` 调用 ``foo(1, y=2)`` 返回 ``OrderedDict([('x', 1), ('y', 2)])``。
    """
    try:
        sig = inspect.signature(wrapped)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound.arguments
    except (TypeError, ValueError):
        return {}


def _render_call(name, arguments):
    """
    根据绑定的实参渲染 ``name(v1, v2, ...)`` 形式的调用串。位置参数与关键字参数
    均只输出其值（不保留参数名），例如 ``foo(1, 2)``。

    :param name: 函数名
    :param arguments: ``_bind_arguments`` 返回的有序字典
    :return: 形如 ``foo(1, 2)`` 的字符串
    """
    values = ", ".join(repr(v) for v in arguments.values())
    return "{}({})".format(name, values)


class _LogFormatter(string.Formatter):
    """扩展 ``str.format``：``{}`` 按位置引用，``{name}`` 按命名引用。

    位置变量顺序固定为 ``(name, level, event, message)``，命名变量同名可取；
    此外模板可直接引用被装饰函数的**形参名**（如 ``{x}`` / ``{y}``）。
    """

    _POSITIONAL_KEYS = ("name", "level", "event", "message")

    def __init__(self, named):
        super().__init__()
        self._named = named
        self._pos_idx = 0

    def get_value(self, key, args, kwargs):
        if key == "":
            # ``{}``：按出现顺序取位置变量
            idx = self._pos_idx
            self._pos_idx += 1
            var_name = self._POSITIONAL_KEYS[idx]
            return self._named.get(var_name, "")
        if isinstance(key, int):
            var_name = self._POSITIONAL_KEYS[key]
            return self._named.get(var_name, "")
        # 命名引用：先查内置变量，再查函数形参名
        return self._named.get(key, "")


def _format_template(template, named):
    """
    用 ``string.Formatter`` 解析模板，``{}`` 按位置、``{key}`` 按命名取变量。
    模板中的 ``{x}`` / ``{y}`` 等会被替换为被装饰函数对应形参的实参值。
    :param template: 带 ``{}`` / ``{name}`` / ``{x}`` 占位符的字符串
    :param named: 变量字典，含内置变量（name/level/event/message）及函数形参名
    :return: 格式化后的字符串
    """
    try:
        return _LogFormatter(named).format(template)
    except (KeyError, IndexError, ValueError):
        # 模板非法时退化为原样返回，避免装饰器导致业务函数报错
        return template


def _normalize_sink(sink, default_out):
    """
    兼容 ``on_enter`` / ``on_exit`` 的三种形态：
      - ``None``           -> 使用默认输出（print / logging.getLogger(__name__).log）
      - ``callable``       -> 直接调用 ``callable(level, name, message)``
      - ``str`` 模板        -> 按 ``{}`` / ``{name}`` / ``{形参名}`` 风格格式化后交给默认输出
    """
    if sink is None:
        def _default_sink(lvl, name, message, arguments=None):
            return default_out(lvl, name, message)
        return _default_sink
    if isinstance(sink, str):
        template = sink

        def _str_sink(lvl, name, message, arguments=None):
            event = "enter" if "enter" in message else "exit"
            rendered = _format_template(
                template,
                {
                    "level": lvl,
                    "name": name,
                    "event": event,
                    "message": message,
                    **(arguments or {}),
                },
            )
            default_out(lvl, name, rendered)

        return _str_sink
    if callable(sink):

        def _callable_sink(lvl, name, message, arguments=None):
            return sink(lvl, name, message)

        return _callable_sink
    return default_out


def std_logging(level=logging.INFO, on_enter=None, on_exit=None):
    """
    日志记录（标准输出）

    进入/退出信息通过 ``on_enter`` / ``on_exit`` 输出，兼容三种形态：

    - 不传（``None``）：默认 ``print("[level]: <enter|exit> name()")``
    - 传可调用 ``callable(level, name, message)``：自行决定如何处置输出
    - 传字符串模板：用 ``{}`` 引用位置变量、``{name}`` 引用函数名，并可直接引用
      **被装饰函数的形参名**（如 ``{x}`` / ``{y}``），例如
      ``"call {name}({x}, {y})"``

    :param level: 日志级别（int 或 str）
    :param on_enter: 进入时输出（可调用或字符串模板），``None`` 时默认打印
    :param on_exit: 退出时输出（可调用或字符串模板），``None`` 时默认打印
    :return: 装饰器
    """
    int_flag = level in LOG_LEVEL_INT
    assert int_flag or level in LOG_LEVEL_STR
    if int_flag:
        level = LOG_LEVEL_MAP_INT2STR[level]

    def _default_out(lvl, name, message):
        print("[{}]: {}".format(lvl, message))

    on_enter = _normalize_sink(on_enter, _default_out)
    on_exit = _normalize_sink(on_exit, _default_out)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        arguments = _bind_arguments(wrapped, args, kwargs)
        # 默认行为与旧版本保持一致：空括号 "enter foo()" / "exit foo()"
        on_enter(level, wrapped.__name__,
                 "enter {}()".format(wrapped.__name__), arguments)
        f = wrapped(*args, **kwargs)
        on_exit(level, wrapped.__name__,
                "exit {}()".format(wrapped.__name__), arguments)
        return f

    return wrapper


def file_logging(level=logging.INFO, on_enter=None, on_exit=None):
    """
    日志记录（文件/标准 logging）

    进入/退出信息通过 ``on_enter`` / ``on_exit`` 输出，兼容三种形态：

    - 不传（``None``）：默认 ``logging.getLogger(__name__).log(level, "<enter|exit> name()")``
    - 传可调用 ``callable(level, name, message)``：自行决定如何处置输出
    - 传字符串模板：用 ``{}`` 引用位置变量、``{name}`` 引用函数名，并可直接引用
      **被装饰函数的形参名**（如 ``{x}`` / ``{y}``），例如
      ``"call {name}({x}, {y})"``

    :param level: 日志级别（int 或 str）
    :param on_enter: 进入时输出（可调用或字符串模板），``None`` 时默认 logging.getLogger(__name__).log
    :param on_exit: 退出时输出（可调用或字符串模板），``None`` 时默认 logging.getLogger(__name__).log
    :return: 装饰器
    """
    str_flag = level in LOG_LEVEL_STR
    assert str_flag or level in LOG_LEVEL_INT
    if str_flag:
        level = LOG_LEVEL_MAP_STR2INT[level]

    def _default_out(lvl, name, message):
        logging.getLogger(__name__).log(lvl, message)

    on_enter = _normalize_sink(on_enter, _default_out)
    on_exit = _normalize_sink(on_exit, _default_out)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        arguments = _bind_arguments(wrapped, args, kwargs)
        # 默认行为与旧版本保持一致：空括号 "enter foo()" / "exit foo()"
        on_enter(level, wrapped.__name__,
                 "enter {}()".format(wrapped.__name__), arguments)
        f = wrapped(*args, **kwargs)
        on_exit(level, wrapped.__name__,
                "exit {}()".format(wrapped.__name__), arguments)
        return f

    return wrapper
