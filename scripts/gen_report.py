
# -*- coding: utf-8 -*-


from astar_devopstool.version_announcement import version_release_announcement_template
from astar_devopstool.common import License, LICENSE_SHORT, Language, Plantform

import astartool

version_dict = {
    'project_name': 'astartool',
    'api': astartool.__version__,
    '版本': astartool.__version__,
    '日期': '2026-06-03',
    '授权协议': LICENSE_SHORT[License.APACHE],
    '开发语言': Language.PYTHON.value,
    '操作系统': "跨平台",
    '分类': "运维工具、工具包",
    '开源地址-gitee': '[https://gitee.com/hoops/astartool]'
                  '(https://gitee.com/hoops/astartool)',
    '开源下载-pypi': '[https://pypi.org/project/astartool/]'
                 '(https://pypi.org/project/astartool/)'
}

content = """
### 新增

1. data_structure

(a). relation-新增关系映射，支持有序/无序、加权/非加权

2. string

(a). 对正则表达式进行优化

3. setuptool

(a). 由于3.12弃用distutils，因此移除在3.10以上版本_version.py中对distutils的依赖,转而依赖setuptools工具包



"""

version_release_announcement_template(version_dict, content=content, file_name="../docs/release/version_release_v0.2.md")
