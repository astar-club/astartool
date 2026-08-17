#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: imagehelper.py
# @time: 2019/6/27 4:16
# @Software: PyCharm


__author__ = 'A.Star'

import base64
import re
from io import BytesIO


def base64_to_image(base64_str, image_path=None):
    """
    base64转图片
    :param base64_str:
    :param image_path:
    :return:
    """
    # Pillow (PIL) is an optional dependency, imported lazily at runtime
    try:
        from PIL import Image
    except ImportError:
        raise ImportError(
            "Pillow is required for base64_to_image. Install it via "
            "`pip install pillow` or `pip install astartool[optional]`."
        )
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img
