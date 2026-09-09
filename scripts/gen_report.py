
# -*- coding: utf-8 -*-


from astar_devopstool.version_announcement import version_release_announcement_template
from astar_devopstool.common import License, LICENSE_SHORT, Language, Plantform

import astartool

version_dict = {
    'project_name': 'astartool',
    'api': astartool.__version__,
    '版本': astartool.__version__,
    '日期': '2026-09-09',
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

1. project._decorators

(a). 新增 singleton 单例类装饰器：按 __init__ 签名归一化 args/kwargs 作为缓存 key，位置参数与关键字参数等价

2. file.file_opt

(a). 新增 read_large_file：按 chunk_size 流式读取并返回生成器，避免一次性载入全部数据
(b). 新增 write_large_file：接受可迭代对象或单一 str/bytes，按块写出，返回写入字节数

### 变更

1. file.file_opt

(a). write_file 新增 mode 参数，支持 mode="bytes" 二进制写入

2. project._profiler

(a). do_cprofile 改用 wrapt 嵌套工厂实现

3. project._project

(a). 删除冗余的旧 project2lines.py 模块，功能以 pathlib 版保留在 _project

4. 打包（setup.py）

(a). long_description 改为读取 README.md 并声明 markdown 内容类型
(b). 短描述改为英文表述

"""

version_release_announcement_template(version_dict, content=content, file_name="../docs/release/version_release_v0.4.md")
