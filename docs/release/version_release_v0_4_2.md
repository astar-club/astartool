# astartool-0.4.2已发布！

**Version: 0.4.2**

**Auth:    ASTARTOOL ROBOT**

**Date:    2026-10-12**


|信息|值|
|:--:|:--:|
|版本|0.4.2|


## 变更摘要（v0.4.2）

本次为 v0.4 的补丁版本，主要增强 `astartool.project` 模块：软著导出链路补齐
PDF 能力，装饰器支持异步函数。

### 新增/变更

- `astartool.project._project` 新增 `project_to_pdf`：输入工程根目录，一键导出
  软著用源代码 PDF。
  - 输出完整源码 PDF（A4、每页固定行数、页眉含软件名+版本+源码总行数、页脚
    页码，reportlab 内置中文字体，无需外部字体文件）；
  - 按软著要求：总页数超过 60 页时，只提交前 30 页 + 后 30 页，另存为
    `source_code_head30_tail30.pdf`；
  - 返回统计信息（总页数、提交版页数、源码总行数、源码文件数）；
  - 目标 txt / PDF 已存在时交互询问是否删除，拒绝则放弃导出（或仅输出完整
    版），不再静默覆盖；确认删除但文件被占用时降级为时间戳文件名。
- `astartool.project._project.project_to_lines` 新增 `compress_blank` /
  `max_blank` 参数（默认开启）：压缩拼接结果中的连续空行（保留至多 1 行）并
  去掉首尾空行，解决源码拼接时文件头尾附加空行导致中间空行过多的问题；
  返回值由 `None` 改为统计字典 `{"file_count", "source_lines"}`。
  `file_to_lines` / `walk` 同步返回源码行数统计。
- `astartool.project._decorators.deprecated_version` /
  `require_optional_import` 支持同步与异步两种函数：装饰 `async def` 函数时
  返回的仍是协程函数，版本校验 / 依赖探测在 `await` 执行时进行。
- `astartool.file.file_opt` 所有路径参数（`file_path` / `path`）的类型注解
  统一为 `Union[str, Path]` 并在 docstring 标注「str 或 pathlib.Path」
  （实现本就通过 `Path(...)` 转换，行为不变）。
- `requirements.txt` 的 `[optional]` 段新增 `reportlab`（`project_to_pdf`
  的可选依赖，`pip install astartool[optional]` 一并安装）。

### 向后兼容

- `project_to_lines` 不传新参数时默认压缩空行（视觉变化，非接口破坏）；传
  `compress_blank=False` 可完全保留旧行为；旧调用方不接收返回值，不受影响。
- `file_to_lines` / `walk` 的返回值由调用方自行决定是否使用，不影响既有调用。

### 示例

```python
from astartool.project import project_to_pdf

info = project_to_pdf(
    src_project='/path/to/project',
    to_dir='softcopyright',
    software_name='My Software',
    version=(1, 0, 0, 'final', 0),
)
# info['pdf']        完整源码 PDF（超过 60 页时另有 info['pdf_part']
#                    = 前 30 页 + 后 30 页的软著提交版）
# info['source_lines'] 源码总行数
```
