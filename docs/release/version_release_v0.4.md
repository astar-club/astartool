# astartool-0.4已发布！

**Version: 0.4**
**Auth:    ASTARTOOL ROBOT**
**Date:    2026-09-09**


|信息|值|
|:--:|:--:|
|版本|0.4|
|日期|2026-09-09|
|授权协议|Apache Software License|
|开发语言|PYTHON|
|操作系统|跨平台|
|分类|运维工具、工具包|
|开源地址-gitee|[https://gitee.com/hoops/astartool](https://gitee.com/hoops/astartool)|
|开源下载-pypi|[https://pypi.org/project/astartool/](https://pypi.org/project/astartool/)|

## 更新内容


### 新增

1. project._decorators

(a). 新增 `singleton` 单例类装饰器：按 `__init__` 签名归一化 `args`/`kwargs`
    作为缓存 key，位置参数与关键字参数等价，支持 `dict`/`list` 等可哈希
    规整，不同构造参数各自对应独立单例。

2. file.file_opt

(a). 新增 `read_large_file`：按 `chunk_size` 流式（分块）读取并返回生成器，
    避免一次性载入全部数据，适用于超大文本/二进制文件。
(b). 新增 `write_large_file`：接受可迭代对象或单一 `str`/`bytes`，按块写出，
    自动创建父目录，返回写入字节数。


### 变更

1. file.file_opt

(a). `write_file` 新增 `mode` 参数，支持 `mode="bytes"` 二进制写入
    （`bytes`/`bytearray`），类型不匹配时抛 `FileOptError("type_error")`。

2. project._profiler

(a). `do_cprofile` 改用 `wrapt` 嵌套工厂实现，执行后始终 `dump_stats(filename)`。

3. project._project

(a). 删除冗余的旧 `project2lines.py` 模块，其功能以 pathlib 版
    `file_to_lines` / `walk` / `project_to_lines` 保留在 `_project` 模块。

4. 打包（setup.py）

(a). `long_description` 改为读取 `README.md` 并声明
    `long_description_content_type='text/markdown'`，使 PyPI 正确渲染。
(b). 短描述 `description` 改为英文表述。
