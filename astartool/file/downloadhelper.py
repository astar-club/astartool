#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: downloadhelper.py
# @time: 2019/6/13 17:33
# @Software: PyCharm
import logging
import os
import urllib.request

from astartool.file.file_opt import FileOptError

# Default chunk size for streaming downloads (64 KiB).
DEFAULT_CHUNK_SIZE = 64 * 2 ** 10


def big_file_download(file_name, file, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    从文件里面下载到file_name路径下
    :param file_name: 文件路径
    :param file: uploadfile对象（django对象）
    :param chunk_size: 文件每次处理大小
    :return:
    """

    def file_iterator(file_name=file_name, file=file, chunk_size=chunk_size):
        with open(file_name, 'wb') as f:
            while True:
                c = file.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    try:
        return file_iterator(file_name)
    except BaseException as e:
        # 没有对应的文件
        logging.error(str(FileNotFoundError))
    return None


def download_large_file(url: str, dest: str, chunk_size: int = DEFAULT_CHUNK_SIZE,
                        timeout: int = 30, headers: dict = None,
                        resume: bool = False, progress_cb=None) -> dict:
    """Stream-download a (potentially large) file from a URL to disk.

    The response body is read in fixed-size chunks so memory usage stays flat
    regardless of file size. An optional progress callback is invoked after each
    chunk. When ``resume`` is ``True`` and ``dest`` already holds a partial
    download, a ``Range`` request continues from the local byte offset if the
    server supports it (HTTP 206); otherwise the download restarts from zero.

    :param url: Source URL to download.
    :param dest: Local destination path (parent dirs are created as needed).
    :param chunk_size: Number of bytes read/written per chunk.
    :param timeout: Socket timeout in seconds for the request.
    :param headers: Extra request headers (e.g. ``{"Authorization": "..."}``).
    :param resume: Enable resumable download via HTTP ``Range`` when possible.
    :param progress_cb: Optional callable ``(downloaded, total)``; ``total`` is
        ``None`` when the server does not advertise ``Content-Length``.
    :return: A dict ``{"dest", "bytes", "resumed", "total"}``.
    :rtype: dict
    :raises FileOptError: on network or HTTP errors, or unsupported resume.
    """
    dest_path = os.path.abspath(dest)
    parent = os.path.dirname(dest_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    existing = 0
    if resume and os.path.isfile(dest_path):
        existing = os.path.getsize(dest_path)

    req_headers = dict(headers or {})
    resumed = False
    if resume and existing > 0:
        req_headers["Range"] = f"bytes={existing}-"
        resumed = True

    request = urllib.request.Request(url, headers=req_headers)
    mode = "ab" if resumed else "wb"

    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            total = resp.headers.get("Content-Length")
            total = int(total) + existing if (total and resumed) else (
                int(total) if total else None)
            with open(dest_path, mode) as out:
                downloaded = existing
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb is not None:
                        progress_cb(downloaded, total)
            final = os.path.getsize(dest_path)
            return {"dest": dest_path, "bytes": final,
                    "resumed": resumed, "total": total}
    except urllib.error.HTTPError as e:
        if resume and e.code == 416:
            raise FileOptError(
                "resume_range_invalid",
                f"server rejected resume Range for {dest_path}: {e}")
        raise FileOptError(
            "http_error", f"HTTP {e.code} while downloading {url}: {e}")
    except urllib.error.URLError as e:
        raise FileOptError(
            "url_error", f"failed to reach {url}: {e.reason}")
    except OSError as e:
        raise FileOptError(
            "io_error", f"failed to write {dest_path}: {e}")
