
# -*- coding: utf-8 -*-


from astar_devopstool.version_announcement import version_release_announcement_template
from astar_devopstool.common import License, LICENSE_SHORT, Language, Plantform

import astartool

version_dict = {
    'project_name': 'astartool',
    'version': astartool.__version__,
    '版本': astartool.__version__,
    '日期': '2025-10-17',
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

(a). mergemap-新增mergemap, 可以对字典进行自定义合并

(b). bisect-增加key_do_func参数, 可选对搜索值是否进行映射操作

2. string

(a). password_check-增加min_length、symbol参数，可选对特殊字符是否支持

3. file

(a). filehelper-新增is_file_using、release_and_delete_file、release_lock、函数, 判断文件是否锁定、解除锁并删除文件、释放锁

4. exception

(a). 新增FileReleaseLockException, 判断文件是否异常

5. number

(a). 新增gcdlcm函数，a和b的最大公约数和最小公倍数



"""

version_release_announcement_template(version_dict, content=content, file_name="../docs/release/version_release_v0.1.4.md")
