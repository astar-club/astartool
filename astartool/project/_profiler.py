# -*- coding: utf-8 -*-
"""
cProfile based profiling decorator (wrapt implementation).

Visualize the result with gprof2dot and Graphviz, e.g.::

    gprof2dot -f pstats "xxx.pfl" | dot -Tpng -o "xxx.png"
"""

import cProfile
import pstats

import wrapt


def do_cprofile(filename):
    """
    cProfile 性能分析装饰器（基于 wrapt 实现）.

    每次调用被装饰函数时启动 cProfile，执行结束后将统计结果写入
    ``filename``（pstats 格式，可用 gprof2dot + Graphviz 生成调用图）。

    :param filename: 性能分析结果输出路径（``.pfl`` / ``.prof`` 等）
    :return: 装饰器
    """
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        profile = cProfile.Profile()
        profile.enable()
        try:
            result = wrapped(*args, **kwargs)
        finally:
            profile.disable()
        stats = pstats.Stats(profile).sort_stats("tottime")
        stats.dump_stats(filename)
        return result

    return wrapper
