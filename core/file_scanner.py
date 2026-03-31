from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable
import threading


@dataclass
class FileEntry:
    path: Path
    name: str
    extension: str
    size: int
    modified: float
    is_dir: bool = False
    ai_suggestion: str = ""
    selected: bool = True

    @property
    def size_human(self) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if self.size < 1024:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024
        return f"{self.size:.1f} TB"


class FileScanner:
    """Scans a directory and returns FileEntry objects."""

    def __init__(self):
        self._stop_event = threading.Event()

    def scan(
        self,
        folder: Path,
        recursive: bool = False,
        extensions: list[str] | None = None,
        on_progress: Callable[[int, FileEntry], None] | None = None,
    ) -> list[FileEntry]:
        self._stop_event.clear()
        entries: list[FileEntry] = []

        glob = "**/*" if recursive else "*"
        paths = sorted(folder.glob(glob))

        for i, p in enumerate(paths):
            if self._stop_event.is_set():
                break
            if p.is_dir():
                continue
            if extensions and p.suffix.lower() not in extensions:
                continue

            try:
                stat = p.stat()
                entry = FileEntry(
                    path=p,
                    name=p.name,
                    extension=p.suffix.lower(),
                    size=stat.st_size,
                    modified=stat.st_mtime,
                )
                entries.append(entry)
                if on_progress:
                    on_progress(i, entry)
            except (PermissionError, OSError):
                continue

        return entries

    def stop(self):
        self._stop_event.set()
