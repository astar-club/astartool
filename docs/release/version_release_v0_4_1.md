# astartool-0.4.1已发布！

**Version: 0.4.1**

**Auth:    ASTARTOOL ROBOT**

**Date:    2026-09-20**


|信息|值|
|:--:|:--:|
|版本|0.4.1|


## 变更摘要（v0.4.1）

本次为 v0.4 的补丁版本，主要增强 `astartool.project._log` 模块中的
`std_logging` / `file_logging` 日志装饰器。

### 新增/变更

- `std_logging` / `file_logging` 新增 `on_enter` / `on_exit` 输出参数，进入/退出
  信息不再固定打印或写日志，而是经由该参数输出。三者兼容：
  - `None`：默认行为（`std_logging` 打印到标准输出；`file_logging` 通过命名 logger
    `logging.getLogger(__name__).log(...)` 输出，取代原先的 `logging.log(...)`）。
  - 可调用 `callable(level, name, message)`：自行决定如何处置输出。
  - 字符串模板：按 `str.format` 风格渲染，支持 `{}` 位置引用与 `{name}` 命名引用，
    **可直接引用被装饰函数的形参名**（如 `{x}` / `{y}`）。
- `file_logging` 默认输出改用具名 logger（`logging.getLogger(__name__)`），便于按
  模块配置 handler 与日志级别，不再写入 root logger。

### 向后兼容

- 不传 `on_enter` / `on_exit` 时，默认输出格式与旧版本保持一致
  （`[level]: enter foo()` / `exit foo()`，括号内不展开参数）。
- 旧的可调用回调签名 `callable(level, name, message)` 仍可正常工作。

### 示例

```python
from astartool.project._log import std_logging

@std_logging(on_enter="foo({x},{y})")
def foo(x, y):
    ...

foo(1, y=2)
# 输出: [INFO]: foo(1,2)
```
