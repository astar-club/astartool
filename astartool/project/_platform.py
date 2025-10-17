# -*- coding: utf-8 -*-


import platform


def is_windows():
    return platform.system().lower() == 'windows'


def is_linux():
    return platform.system().lower() == 'linux'


def is_64bit():
    return platform.machine().endswith("64")


def is_32bit():
    return platform.machine().endswith("32")
