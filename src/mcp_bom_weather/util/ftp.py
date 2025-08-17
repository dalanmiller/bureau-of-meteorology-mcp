from __future__ import annotations

import io
import time
from collections.abc import Callable
from ftplib import FTP
from typing import TypeVar

from ..config import FTP_TIMEOUT_SECS, MAX_RETRIES


class FtpClient:
    def __init__(self, host: str) -> None:
        self.host = host

    def _with_retries(self, fn: Callable[[], T]) -> T:  # type: ignore[name-defined]
        delay = 0.5
        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return fn()
            except Exception as exc:
                last_exc = exc
                if attempt >= MAX_RETRIES:
                    break
                time.sleep(delay)
                delay = min(delay * 2, 5.0)
        assert last_exc is not None
        raise last_exc

    def _connect(self) -> FTP:
        ftp = FTP()
        ftp.connect(self.host, timeout=FTP_TIMEOUT_SECS)
        ftp.login()  # anonymous
        return ftp

    def list_files(self, directory: str) -> list[str]:
        def op() -> list[str]:
            with self._connect() as ftp:
                ftp.cwd(directory)
                return ftp.nlst()

        return self._with_retries(op)

    def fetch_text(self, path: str, encoding: str = "utf-8") -> str:
        def op() -> str:
            with self._connect() as ftp:
                buf = io.BytesIO()
                ftp.retrbinary(f"RETR {path}", buf.write)
                return buf.getvalue().decode(encoding, errors="replace")

        return self._with_retries(op)


T = TypeVar("T")
