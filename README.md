# astartool

[![version](https://img.shields.io/pypi/v/astartool.svg)](https://pypi.python.org/pypi/astartool)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FASTARCHEN%2Fastartool.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FASTARCHEN%2Fastartool?ref=badge_shield)
[![gitee](https://gitee.com/hoops/astartool/badge/star.svg)](https://gitee.com/hoops/astartool/stargazers)
[![github](https://img.shields.io/github/stars/ASTARCHEN/astartool)](https://img.shields.io/github/stars/ASTARCHEN/astartool)
[![download](https://img.shields.io/pypi/dm/astartool.svg?cacheSeconds=86400)](https://pypi.org/project/astartool)
[![wheel](https://img.shields.io/pypi/wheel/astartool.svg)](https://pypi.python.org/pypi/astartool)
[![CodeFactor](https://www.codefactor.io/repository/github/astarchen/astartool/badge/main)](https://www.codefactor.io/repository/github/astarchen/astartool/overview/main)
![status](https://img.shields.io/pypi/status/astartool.svg)
[![wiki](https://img.shields.io/badge/wiki-v0.2.0-green)](https://github.com/ASTARCHEN/astartool/wiki)

A.Star私房工具包

唉~ 写了辣么多代码，总觉得过于臃肿。
我把简单的代码能重复利用的摘出来作为工具包，以后就引用他了

## 一、安装
- pip 安装
```commandline
pip install astartool
```
- 源码安装
1. 从源码库里面下载合适的版本
- gitee: https://gitee.com/hoops/astartool
- github: https://github.com/ASTARCHEN/astartool

2. 下载依赖包
```commandline
pip install -r requirements.txt
```
3. 安装rar工具【可选】
filehelper可选
从 [链接](https://www.rarlab.com/download.htm) 下载rar工具并加将rar工具设置进环境变量

## 二、源码结构

目前此代码包含以下几部分:

### 1. data_structure - 数据结构

| 类/函数 | 说明 |
|---------|------|
| `KeyMap` | 双向键值映射（通过key查value，也可通过value反向查key） |
| `DataNode` / `LinkedList` / `Pointer` | 双向循环链表及其节点/指针 |
| `LinkedQueue` | 基于链表的线程安全队列 |
| `LazyMap` / `MutableLazyMap` | 惰性求值映射，值首次访问时才计算，线程安全 |
| `MergeMap` | 合并映射，同一key的多个value通过自定义函数合并 |
| `Heap` | 基于heapq的堆封装，支持自定义键函数 |
| `UnionFind` | 并查集（路径压缩+按秩合并） |
| `RelationMap` | 关系映射，支持有序/无序、加权/非加权 |
| `bisect_left` / `bisect_right` / `insort_left` / `insort_right` | 带自定义键函数的二分查找与插入 |

### 2. error - 错误

| 类 | 说明 |
|----|------|
| `MethodNotFoundError` | 方法未找到错误 |
| `ParameterError` | 参数错误 |
| `ParameterTypeError` | 参数类型错误 |
| `ParameterValueError` | 参数值错误 |
| `LazyDictionaryError` | 惰性字典基类异常 |
| `CircularReferenceError` | 循环引用错误 |
| `ConstantRedefinitionError` | 常量重定义错误 |

### 3. exception - 异常

| 类 | 说明 |
|----|------|
| `AstarToolException` | astartool 基础异常类 |
| `FileReleaseLockException` | 文件释放锁异常 |

### 4. file - 文件处理

| 类/函数 | 说明 |
|---------|------|
| `CalcSha1` / `CalcMD5` / `CalcSM3` / `CalcHash` | 文件哈希计算（SHA1/MD5/SM3/通用） |
| `file_extension` / `get_file_name` | 文件路径工具 |
| `rename` | 通过哈希重命名文件 |
| `is_file_using` / `release_lock` / `release_and_delete_file` | 文件锁检测与释放 |
| `CompressionType` / `extractall` / `namelist` | 压缩解压（支持zip/rar/tar/tar.gz/tar.bz2/tar.xz） |
| `to_excel` | 数据导出为Excel |
| `big_file_download` | 大文件分块下载 |
| `base64_to_image` | Base64转图片 |

### 5. number - 数字处理

| 函数 | 说明 |
|------|------|
| `ishex` | 判断是否为16进制字符串 |
| `gcd` / `lcm` / `gcdlcm` | 最大公约数 / 最小公倍数 |
| `get_primes` | 获取小于n的所有质数 |
| `prime_factorization` | 质因数分解 |
| `is_prime` | Miller-Rabin快速素数判定 |
| `rotate_left` | 循环左移位运算 |
| `equals_zero` / `equals_zero_all` / `equals_zero_any` | 矩阵零元素判断 |

### 6. project - 项目工具

| 类/函数 | 说明 |
|---------|------|
| `std_logging` / `file_logging` | 日志装饰器（标准输出/文件） |
| `cost_time` | 函数耗时统计装饰器 |
| `do_cprofile` | cProfile性能分析装饰器 |
| `is_windows` / `is_linux` / `is_64bit` / `is_32bit` | 平台检测 |
| `project_to_lines` / `walk` | 项目文件遍历导出（软著申请用） |
| `model_to_doc` / `model_to_dict` | Django模型文档生成 |
| `url_to_interface_template` | Django接口模板生成 |
| `auto_title` | 文档头自动生成（支持md/rst） |

### 7. random - 随机数

| 函数 | 说明 |
|------|------|
| `random_string` | 随机生成字符串 |
| `random_digit_string` | 随机生成n位数字串 |
| `random_hex_string` | 随机生成n位16进制字符串 |
| `generate_password` | 随机生成密码 |
| `random_ip` | 随机生成IPv4地址 |
| `security_random_hex` | 基于国密SM3的KDF随机数 |

### 8. setuptool - 打包工具

| 函数 | 说明 |
|------|------|
| `get_version` / `get_main_version` / `get_complete_version` | 版本号处理 |
| `get_git_changeset` | 获取最新git提交时间戳 |
| `setup` | 包装setuptools.setup |
| `load_install_requires` | 读取requirements.txt依赖 |

### 9. string - 字符串处理

| 函数 | 说明 |
|------|------|
| `is_email` | 判断是否为邮箱 |
| `is_ip` | 判断是否为IPv4地址 |
| `is_mobile` | 判断是否为手机号 |
| `is_url` | 判断是否为URL |
| `is_valid_number` | 判断是否为有效数字 |
| `has_Chinese` | 判断是否包含中文字符 |
| `generate_number` / `check_number` | 生成/校验带时间戳编号 |
| `force_bytes` / `force_str` | str与bytes强制转换 |
| `to_binary` / `to_text` | six兼容的编码转换 |
| `check_password` / `check_length` / `check_contain_upper` 等 | 密码强度检查 |


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FASTARCHEN%2Fastartool.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FASTARCHEN%2Fastartool?ref=badge_large)

