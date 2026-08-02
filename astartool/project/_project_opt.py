# -*- coding: utf-8 -*-

"""Project / shell execution helpers (decoupled from any MCP/registry layer).

This module provides standalone functions for executing scripts and installing
Python packages on the local machine, extracted from the script-execution logic
in snowland_aitool_client.tools (run_shell / install_python_packages). They
carry no dependency on the MCP registry, the McpResult envelope, or the
agent-core sandbox guard: ``workspace`` is passed in explicitly and results are
returned as plain dicts so the functions can be reused anywhere.

Functions:
    :func:`run_shell`: execute a shell command inside a workspace sandbox.
    :func:`install_packages`: install Python packages via pip (download + install).
"""

import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Optional

# Bounded-result caps.
MAX_SHELL_OUTPUT = 16 * 1024
SHELL_TIMEOUT_SEC = 120

# run_shell accepts a safe subset (build / test / lint / VCS read) as
# NON-destructive: these may be run directly (no system shell). Anything else
# (rm/del/curl/wget/ssh/...) is routed through the system shell and must be
# confirmed by the caller before the call is dispatched.
SHELL_ALLOW_LIST = {
    # JVM / Java build
    "gradlew", "gradle", "mvn", "java", "javac", "sbt", "scala", "scalac",
    "kotlin", "kotlinc",
    # Node / front-end
    "npm", "yarn", "pnpm", "node", "bun", "rush",
    "eslint", "prettier", "tsc", "webpack", "vite", "rollup",
    # Python
    "python", "python3", "pip", "pip3", "pytest", "poetry", "uv", "tox",
    "conda", "mamba",
    # Go / Rust / C-C++ / .NET
    "go", "cargo", "rustc", "rustdoc", "make", "cmake", "ctest",
    "dotnet", "bazel", "ninja",
    # Other languages
    "ruby", "rake", "perl", "php", "swift", "dart", "lua", "tclsh",
    "julia",
    # VCS
    "git",
    # Shell interpreters
    "sh", "bash",
}

GIT_READONLY_SUBCOMMANDS = {
    "status", "diff", "log", "show", "branch", "remote", "rev-parse", "ls-files",
}

# Commands whose blast radius is the whole machine / OS and which are never
# offered for confirmation, even if the user would approve. They escape the
# workspace chroot and are effectively unrecoverable.
SHELL_NEVER_ALLOW = {"mkfs", "format", "shutdown", "reboot", "halt", "poweroff", "dd"}


def tokenize(command: str) -> list:
    """Split a shell command string into tokens, honoring quotes.

    :param command: The raw shell command string.
    :return: A list of tokens with quoted spans preserved as single units.
    :rtype: list
    """
    out = []
    sb = []
    quote = ""
    for c in command:
        if quote:
            if c == quote:
                quote = ""
            else:
                sb.append(c)
        elif c in ('"', "'"):
            quote = c
        elif c.isspace():
            if sb:
                out.append("".join(sb))
                sb.clear()
        else:
            sb.append(c)
    if sb:
        out.append("".join(sb))
    return out


def leading_executable(head: str) -> str:
    """Normalize a command head such as ``./gradlew`` / ``gradlew.bat`` to its key.

    :param head: The first token (or executable name) of the command.
    :return: The lower-cased executable key with path and known extensions stripped.
    :rtype: str
    """
    s = head.replace("\\", "/").split("/")[-1]
    for ext in (".bat", ".cmd", ".exe", ".sh"):
        if s.endswith(ext):
            s = s[: -len(ext)]
            break
    return s.lower()


def is_forbidden(tokens: list) -> bool:
    """Check whether a command's damage cannot be bounded to the workspace.

    :param tokens: The tokenized command.
    :return: ``True`` if the command is machine-wide / unrecoverable and must be
        refused outright.
    :rtype: bool
    """
    exe = tokens[0].lower()
    if exe in SHELL_NEVER_ALLOW:
        return True
    if exe in {"rm", "del", "rmdir"} and any(
        t in ("/", "/*", "/*.*", "\\") for t in tokens
    ):
        return True
    return False


def shell_command(command: str) -> str:
    """Build the system-shell invocation string for a raw command.

    :param command: The raw command to wrap.
    :return: The platform-specific shell invocation (``cmd /c`` on Windows).
    :rtype: str
    """
    if sys.platform.startswith("win"):
        return f'cmd /c "{command}"'
    return command


def run_shell(command: str, workspace: str, cwd: str = "",
              safe_path_fn: Optional[Callable[[str], Optional[Path]]] = None,
              timeout: int = SHELL_TIMEOUT_SEC) -> dict:
    """Run a shell command inside the workspace sandbox and return a result dict.

    Safety model (mirrors the IDE design doc):
      * allow-listed build/test/VCS-read commands run directly (non-destructive);
      * everything else is routed through the system shell and must be confirmed
        by the caller before dispatch;
      * machine-wide / unrecoverable commands are refused outright.

    :param command: The shell command string.
    :param workspace: Root the command is allowed to touch (also the default cwd).
    :param cwd: Optional working directory (relative to ``workspace`` or absolute).
    :param safe_path_fn: Optional callable ``str -> Path | None`` used as a sandbox
        guard. When ``None``, no path check is performed (the caller is
        responsible for the sandbox). Supplying a function such as
        ``snowland_agent_core.core.safety.safe_path`` reproduces a workspace
        guard that rejects paths escaping ``workspace``.
    :param timeout: Per-command timeout in seconds.
    :return: A plain dict with either ``{"ok": True, "data": {"exit", "stdout",
        "truncated"}}`` on success, or ``{"ok": False, "error": {"code",
        "message"}}`` on failure.
    :rtype: dict
    """
    if not command or not command.strip():
        return {"ok": False, "error": {"code": "bad_command", "message": "empty command"}}
    tokens = tokenize(command)
    if not tokens:
        return {"ok": False, "error": {"code": "bad_command", "message": "empty command"}}
    exe = leading_executable(tokens[0])
    in_allow_list = exe in SHELL_ALLOW_LIST
    git_readonly = exe == "git" and (
        len(tokens) <= 1 or tokens[1].lower() in GIT_READONLY_SUBCOMMANDS
    )
    if is_forbidden(tokens):
        return {
            "ok": False,
            "error": {
                "code": "command_forbidden",
                "message": f"command forbidden (machine-wide / unrecoverable): {exe}",
            },
        }

    base = Path(workspace) if workspace else Path.cwd()
    if cwd:
        cand = Path(cwd)
        if not cand.is_absolute():
            cand = base / cand
        if safe_path_fn is not None:
            checked = safe_path_fn(str(cand))
            if checked is None:
                base = Path(base)
            else:
                base = checked
    destructive = not (in_allow_list and git_readonly)
    try:
        proc = subprocess.run(
            shell_command(command) if destructive else tokens,
            cwd=str(base),
            shell=destructive,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": {"code": "timeout", "message": f"command timed out after {timeout}s"}}
    except FileNotFoundError:
        return {"ok": False, "error": {"code": "interpreter_missing", "message": f"command not found: {exe}"}}
    output = proc.stdout or ""
    truncated = len(output.encode("utf-8")) > MAX_SHELL_OUTPUT
    shown = output if not truncated else output[:MAX_SHELL_OUTPUT]
    return {"ok": True, "data": {"exit": proc.returncode, "stdout": shown, "truncated": truncated}}


# pip install timeout in seconds.
PIP_TIMEOUT_SEC = 300


def install_packages(requirements_file: str = "", packages: Optional[List[str]] = None,
                     interpreter: str = "", timeout: int = PIP_TIMEOUT_SEC) -> dict:
    """Install Python packages via pip and return a result dict.

    This is the "download / install Python third-party packages" action. It only
    runs pip and returns the captured stdout/stderr plus the exit code; it
    performs no workspace file I/O and does not need the sandbox path guard, so
    it is left unguarded here (pass ``requirements_file`` / ``packages`` you
    already trust).

    :param requirements_file: Path to a requirements.txt to install from.
    :param packages: List of PEP 508 specs, e.g. ``['aider', 'litellm>=1.0']``.
    :param interpreter: Python interpreter to run pip with (defaults to
        ``sys.executable``, the one running this code).
    :param timeout: pip timeout in seconds.
    :return: A plain dict: on success ``{"ok": True, "data": {"returncode",
        "stdout", "stderr"}}``; on failure ``{"ok": False, "error": {"code",
        "message"}}``.
    :rtype: dict
    """
    pkgs = list(packages or [])
    if not requirements_file and not pkgs:
        return {"ok": False, "error": {"code": "nothing_to_install",
                                        "message": "provide requirements_file and/or packages"}}

    if not requirements_file:
        # Default requirements file: this module lives at
        # astartool/project/_project_opt.py, so the project's own
        # astartool/requirements.txt is one directory up.
        default_req = Path(__file__).resolve().parent.parent / "requirements.txt"
        if default_req.is_file():
            requirements_file = str(default_req)

    py = interpreter or sys.executable
    cmd = [py, "-m", "pip", "install"]
    if requirements_file:
        cmd += ["-r", requirements_file]
    cmd += pkgs

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": {"code": "pip_timeout",
                                        "message": f"pip install exceeded {timeout}s"}}
    except FileNotFoundError:
        return {"ok": False, "error": {"code": "interpreter_missing",
                                        "message": f"interpreter not found: {py}"}}

    payload = {
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "").strip()[-4000:],
        "stderr": (proc.stderr or "").strip()[-4000:],
    }
    if proc.returncode == 0:
        return {"ok": True, "data": payload}
    return {"ok": False, "error": {"code": "pip_failed",
                                    "message": f"pip install failed (rc={proc.returncode})"}}
