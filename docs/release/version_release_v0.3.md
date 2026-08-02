# astartool-0.3已发布！

**Version: 0.3**
**Auth:    ASTARTOOL ROBOT**
**Date:    2026-08-02**


|信息|值|
|:--:|:--:|
|版本|0.3|
|日期|2026-08-02|
|授权协议|Apache Software License|
|开发语言|PYTHON|
|操作系统|跨平台|
|分类|运维工具、工具包|
|开源地址-gitee|[https://gitee.com/hoops/astartool](https://gitee.com/hoops/astartool)|
|开源下载-pypi|[https://pypi.org/project/astartool/](https://pypi.org/project/astartool/)|

## 更新内容


### 新增

1. file.file_opt

(a). 新增文件助手模块，提供 `read_file` / `write_file` / `list_dir` / `search_content`
     / `list_archive`，统一通过 `FileOptError` 报告错误。

(b). 新增 `edit_file`：基于精确匹配的批量替换（多组 `old`/`new` 列表）或 `content`
     全量覆盖。

2. file.downloadhelper

(a). 新增 `download_large_file`：URL 流式下载，支持断点续传（`Range`/HTTP 206）
     与进度回调。

3. project._project_opt

(a). 新增 `run_shell`：与 MCP/注册表解耦的本地 shell 执行助手，带白名单/确认/拒绝
     三级安全模型。
(b). 新增 `install_packages`：通过 pip 安装依赖并以 dict 返回结果。

4. error.file_opt_error

(a). 新增 `FileOptError` 异常，作为 file_opt / downloadhelper 的统一错误载体。


### 变更

1. number._number

(a). `is_prime` 改用 `secrets.randbelow`（密码学安全随机），并新增 `number < 2`
     早返回；`is_prime(0)` / `is_prime(1)` 现正确返回 `False`。

2. setuptool._tool

(a). `setup()` 兼容标准 `version=` 键与旧式 `api=` 元组键，修复
     `pip install -e .` / `setup.py develop` 的 `KeyError`。


### 依赖

1. requirements.txt 移除未使用的 `scipy` 依赖。
