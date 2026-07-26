import subprocess
from pathlib import Path

from astartool.error.file_opt_error import FileOptError
from astartool.error import ParameterValueError
from astartool.file.compresshelper import namelist


def read_file(file_path: str, start: str = "0", end: str = "end",
              limit: int = 0) -> str:
    """Read a text file inside the workspace and return its content.

    start: 0-based first line to include (default 0).
    end: 0-based last line (exclusive), or 'end' for the whole tail.
    limit: max number of returned lines (0 = no extra cap).
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

    Parent directories are created as needed. Returns the number of
    characters written.
    """
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return len(content)


def list_dir(path: str = ".") -> list:
    """List directory entries (files and subdirs) inside the workspace.

    Returns a list of {"type": "dir"|"file", "name": str} dicts sorted by
    name.
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

    Returns matches as ``file:line:text`` lines, or ``(no matches)``. Uses
    ripgrep when available and falls back to a pure-Python substring scan
    (capped at 200 matches) otherwise.
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


def list_archive(file_path: str, sort: bool = True) -> list:
    """List the file entries inside a compressed archive under the workspace.

    Supports zip/rar/tar/tar.gz/tar.bz2/tar.xz via astartool's namelist.
    Directories are excluded for tar/rar (only file members are returned).
    Returns the list of entry names.
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
