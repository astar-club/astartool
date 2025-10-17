# -*- coding: utf-8 -*-

import cProfile
import pstats
import os
import wrapt


def do_cprofile(filename):
    # 性能分析装饰器定义
    # Graphviz 下载地址： https://www.graphviz.org/download/
    # 配置环境变量以后
    # pip install gprof2dot
    # gprof2dot -f pstats "D:\fcson.pfl" | "D:\Program Files\Graphviz2.38\bin\dot" -Tpng -o "D:\xxx.png"

    def wrapper(func):
        def profiled_func(*args, **kwargs):
            # Flag for do profiling or not.
            profile = cProfile.Profile()
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            # Sort stat by internal time.
            sortby = "tottime"
            ps = pstats.Stats(profile).sort_stats(sortby)
            ps.dump_stats(filename)
            return result

        return profiled_func

    return wrapper
