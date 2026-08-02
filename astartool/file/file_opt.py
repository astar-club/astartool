import subprocess
from pathlib import Path
from typing import List, Optional, Union

from astartool.error.file_opt_error import FileOptError
from astartool.error import ParameterValueError
from astartool.file.compresshelper import namelist


def read_file(file_path: str, start: str = "0", end: str = "end",
              limit: int = 0) -> str:
    """Read a text file inside the workspace and return its content.

    :param file_path: Path to the text file to read.
    :param start: 0-based first line to include (default ``"0"``).
    :param end: 0-based last line (exclusive), or ``"end"`` for the whole tail.
    :param limit: Max number of returned lines (``0`` = no extra cap).
    :return: The selected file content as a string.
    :rtype: str
    """
    p = Path(file_path)
    if not p.is_file():
        raise FileOptError(
            "not_readable", f"not a readable file in workspace: {file_path}")

    with open(p, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    start_line = int(start)
    end_line = int(end) if end != "end" else len(lines)
    selected = lines[start_line:end_line]
    if limit and limit > 0:
        selected = selected[:limit]
    return "".join(selected)


def write_file(file_path: str, content: str) -> int:
    """Overwrite a workspace file with ``content`` (full write).

    Parent directories are created as needed.

    :param file_path: Path to the file to write.
    :param content: The full text content to write.
    :return: The number of characters written.
    :rtype: int
    """
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
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
