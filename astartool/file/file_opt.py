import subprocess
from pathlib import Path
from typing import List, Optional, Union

from astartool.error.file_opt_error import FileOptError
from astartool.error import ParameterValueError
from astartool.file.compresshelper import namelist


def read_large_file(file_path: str, chunk_size: int = 8 * 1024 * 1024,
                    mode="str", encoding="utf-8"):
    """流式读取大文件，按分块返回内容，避免一次性将全部数据载入内存。

    与 :func:`read_file` 不同，本函数不读取完整文件后再切片，而是按
    ``chunk_size`` 分块（流式）读取。``mode="str"`` 时按文本模式逐块读取
    并返回生成器（每次产出 `str`）；其他 mode 按二进制模式读取并返回
    生成器（每次产出 `bytes`）。

    适用于超大文本/二进制文件的增量处理（如逐块分析、转发），调用方
    通过遍历返回的生成器按需消费数据，无需在内存中持有整份内容。

    :param file_path: 待读取的文件路径。
    :param chunk_size: 单次读取的字节数（文本模式下按字符读取同样大小）。
    :param mode: ``"str"`` 按文本读取，其他值（如 ``"bytes"``）按二进制读取。
    :param encoding: 文本模式下的文件编码。
    :return: 一个生成器，逐个产出分块内容（str 或 bytes）。
    :raises FileOptError: 文件不可读或读取过程中出错。
    """
    p = Path(file_path)
    if not p.is_file():
        raise FileOptError("not_a_file", "Path is not a regular file: %s" % p)
    try:
        if mode == "str":
            with p.open("r", encoding=encoding, errors="replace") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        else:
            with p.open("rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
    except OSError as e:
        raise FileOptError("read_error", "Failed to read large file %s: %s" % (p, e))


def write_large_file(file_path: str, data, chunk_size: int = 8 * 1024 * 1024,
                     mode="str", encoding="utf-8") -> int:
    """流式写入大文件，按分块写入数据，避免一次性持有全部内容。

    与 :func:`write_file` 不同，本函数接受一个可迭代对象（生成器/列表等）
    作为 ``data``，按 ``chunk_size`` 分块写入磁盘；也兼容直接传入单一的
    ``str`` / ``bytes``。写入前会确保父目录存在。返回写入的字节数（文本
    模式按 ``encoding`` 编码后计算，二进制模式直接累加）。

    适用于超大内容的增量写出（如逐块生成、流式下载落盘）。

    :param file_path: 目标文件路径。
    :param data: 待写入的数据，可为 str/bytes，或产生 str/bytes 的可迭代对象。
    :param chunk_size: 单次写入的字节数（仅当 ``data`` 为单一 str/bytes 时用于分块）。
    :param mode: ``"str"`` 按文本写入，其他值按二进制写入。
    :param encoding: 文本模式下的文件编码。
    :return: 实际写入的字节数。
    :raises FileOptError: 路径非法或写入过程中出错。
    """
    p = Path(file_path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise FileOptError("mkdir_error", "Failed to create dir for %s: %s" % (p, e))

    total = 0
    try:
        # 兼容单一 str/bytes：包装为可迭代对象后再统一处理
        if isinstance(data, (str, bytes, bytearray)):
            chunks = (data[i:i + chunk_size]
                      for i in range(0, len(data), chunk_size))
        else:
            chunks = data

        if mode == "str":
            with open(p, "w", encoding=encoding) as f:
                for chunk in chunks:
                    if isinstance(chunk, bytes):
                        chunk = chunk.decode(encoding, errors="replace")
                    f.write(chunk)
                    total += len(chunk.encode(encoding))
        else:
            with open(p, "wb") as f:
                for chunk in chunks:
                    if isinstance(chunk, str):
                        chunk = chunk.encode(encoding)
                    f.write(chunk)
                    total += len(chunk)
    except OSError as e:
        raise FileOptError("write_error", "Failed to write large file %s: %s" % (p, e))
    return total


def read_file(file_path: str, start: str = "0", end: str = "end",
              limit: int = 0, mode="str", encoding="utf-8") -> Union[str, bytes]:
    """Read a text file inside the workspace and return its content.

    :param file_path: Path to the text file to read.
    :param start: 0-based first line to include (default ``"0"``).
    :param end: 0-based last line (exclusive), or ``"end"`` for the whole tail.
    :param mode: Output content mode; ``"str"`` reads as text (default),
        any other value (e.g. ``"bytes"``) reads as binary.
    :param limit: Max number of returned lines (``0`` = no extra cap).
    :param encoding: Encoding of file (default ``"utf-8"``).
    :return: The selected file content; a ``str`` when ``mode="str"``,
        otherwise ``bytes``.
    :rtype: str or bytes
    """
    p = Path(file_path)
    if not p.is_file():
        raise FileOptError(
            "not_readable", f"not a readable file in workspace: {file_path}")

    if mode == "str":
        with open(p, "r", encoding=encoding, errors="replace") as f:
            lines = f.readlines()
        start_line = int(start)
        end_line = int(end) if end != "end" else len(lines)
        selected = lines[start_line:end_line]
        if limit and limit > 0:
            selected = selected[:limit]
        # ``"".join`` preserves original line endings (incl. the trailing newline),
        # so a full-file read (start="0", end="end", limit=0) yields exactly the
        # same string as ``Path.read_text()`` / ``file.read()``. This keeps the
        # return consistent with ``astartool.setuptool._tool.read_file``.
        return "".join(selected)
    else:
        with open(p, "rb") as f:
            lines = f.read()
        return lines


def write_file(file_path: str, content: Union[str, bytes, bytearray], mode="str", encoding="utf-8") -> int:
    """Overwrite a workspace file with ``content`` (full write).

    Parent directories are created as needed. ``mode="str"`` 时按文本写入
    （``content`` 应为 ``str``，返回写入字符数）；其他值（如 ``"bytes"``）
    时按二进制写入（``content`` 应为 ``bytes``/``bytearray``，返回写入字节数）。

    :param file_path: Path to the file to write.
    :param content: The full content to write (``str`` in text mode, ``bytes``/``bytearray`` in binary mode).
    :param mode: ``"str"`` 按文本写入，其他值按二进制写入。
    :param encoding: 文本模式下的文件编码。
    :return: 文本模式返回字符数，二进制模式返回字节数。
    :rtype: int
    :raises FileOptError: 二进制模式下 ``content`` 非 bytes，或写入失败。
    """
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if mode == "str":
        if not isinstance(content, str):
            raise FileOptError(
                "type_error",
                "content must be str in text mode, got %s" % type(content).__name__)
        p.write_text(content, encoding=encoding)
        return len(content)
    else:
        if not isinstance(content, (bytes, bytearray)):
            raise FileOptError(
                "type_error",
                "content must be bytes/bytearray in binary mode, got %s" % type(content).__name__)
        p.write_bytes(bytes(content))
        return len(content)


def list_dir(path: str = ".") -> list:
    """List directory entries (files and subdirs) inside the workspace.

    :param path: The directory path to list.
    :return: A list of ``{"type": "dir"|"file", "name": str}`` dicts sorted by
        name.
    :rtype: list
    """
    p = Path(path)
    if not p.is_dir():
        raise FileOptError("not_a_dir", f"not a dir in workspace: {path}")
    return [
        {"type": "dir" if c.is_dir() else "file", "name": c.name}
        for c in sorted(p.iterdir())
    ]


def search_content(pattern: str, path: str = ".") -> str:
    """Grep for a regex pattern under a workspace path.

    :param pattern: The regex pattern to search for.
    :param path: The root path to search under.
    :return: Matches as ``file:line:text`` lines, or ``(no matches)``. Uses
        ripgrep when available and falls back to a pure-Python substring scan
        (capped at 200 matches) otherwise.
    :rtype: str
    """
    target = Path(path)
    try:
        out = subprocess.run(
            ["rg", "--line-number", "--hidden", "--glob", "!.git",
             pattern, str(target)],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout or "(no matches)"
    except FileNotFoundError:
        results = []
        for f in target.rglob("*"):
            if f.is_file() and ".git" not in f.parts:
                try:
                    for i, line in enumerate(
                        f.read_text(errors="ignore").splitlines(), 1
                    ):
                        if pattern in line:
                            results.append(f"{f}:{i}:{line}")
                except Exception:
                    pass
        return "\n".join(results[:200]) or "(no matches)"


def list_archive(file_path: Union[str | Path], sort: bool = True) -> list:
    """List the file entries inside a compressed archive under the workspace.

    Supports zip/rar/tar/tar.gz/tar.bz2/tar.xz via astartool's namelist.
    Directories are excluded for tar/rar (only file members are returned).

    :param file_path: Path to the archive file.
    :param sort: Whether to sort the returned entry names.
    :return: The list of archive entry names.
    :rtype: list
    """

    p = Path(file_path)
    if not p.is_file():
        raise FileOptError(
            "not_readable", f"not a readable file in workspace: {file_path}")
    try:
        return namelist(str(p), sort=sort)
    except ParameterValueError as e:
        raise FileOptError(
            "unsupported_archive", f"unsupported or non-archive file: {e}")
    except Exception as e:  # BadZipFile / RarFile error / tar read error / etc.
        raise FileOptError("archive_error", f"failed to read archive: {e}")


def edit_file(file_path: Union[str, Path], old: Optional[List[str]] = None,
              new: Optional[List[str]] = None, content: str = "") -> dict:
    """Edit a workspace file via exact replacement or full overwrite.

    Two mutually exclusive modes are supported:

    * ``{old, new}``: replace the **first exact occurrence** of each ``old[i]``
      with ``new[i]``. ``old`` and ``new`` must be equal-length lists. A missing
      match raises :class:`FileOptError` with code ``edit_no_match`` so the
      caller can re-read and retry.
    * ``{content}``: full overwrite of the file (parent dirs are created).

    Passing a ``diff`` payload is intentionally unsupported here; callers that
    need unified-diff application should use a dedicated patch tool instead.

    :param file_path: Path to the file to edit.
    :param old: List of exact texts to locate and replace. ``None``/empty
        disables replace mode.
    :param new: List of replacement texts, parallel to ``old``.
    :param content: Full text used to overwrite the file (when ``old`` is empty).
    :return: A dict ``{"path": str, "bytes": int, "mode": "replace"|"overwrite"}``.
    :rtype: dict
    :raises FileOptError: on missing file, length mismatch, no match for
        ``old``, or invalid args.
    """
    if old:
        if new is None or len(old) != len(new):
            raise FileOptError(
                "length_mismatch",
                "edit_file: 'old' and 'new' must be equal-length lists")
        p = Path(file_path)
        if not p.is_file():
            raise FileOptError("not_a_file", f"not a file: {file_path}")
        text = p.read_text(encoding="utf-8")
        for o, n in zip(old, new):
            idx = text.find(o)
            if idx < 0:
                raise FileOptError(
                    "edit_no_match",
                    f"no match for the given 'old' text in {file_path}; file "
                    f"unchanged. Re-read the file and resend edit_file with the "
                    f"EXACT current text as 'old'")
            text = text[:idx] + n + text[idx + len(o):]
        p.write_text(text, encoding="utf-8")
        return {"path": str(p), "bytes": len(text), "mode": "replace"}

    if not content:
        raise FileOptError(
            "missing_argument",
            "provide {old, new} for replacement or {content} for overwrite")

    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"path": str(p), "bytes": len(content), "mode": "overwrite"}
