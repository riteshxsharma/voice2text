from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Callable

from .config import AppConfig
from .conversion import convert_transcript
from .storage import ProcessedManifest, file_sha256, slugify_filename, unique_destination


@dataclass
class ProcessResult:
    source_path: Path
    archived_path: Path
    emacs_path: Path
    latex_path: Path


class TranscriptProcessor:
    def __init__(self, config: AppConfig, log_callback: Callable[[str], None] | None = None) -> None:
        self.config = config
        self.log_callback = log_callback or (lambda _: None)
        self.config.ensure_directories()
        self.manifest = ProcessedManifest(self.config.logs_path / "processed_manifest.json")
        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._stability_cache: dict[str, tuple[int, float]] = {}

    def start(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._stop_event.clear()
        self._worker = threading.Thread(target=self._run_loop, daemon=True)
        self._worker.start()
        self.log_callback("Background processor started.")

    def stop(self) -> None:
        self._stop_event.set()
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=3)
        self.log_callback("Background processor stopped.")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            for path in sorted(self.config.incoming_path.glob("*.txt")):
                try:
                    if self._is_stable(path):
                        self.process_file(path)
                except Exception as exc:  # pragma: no cover - defensive UI loop
                    self._log_event("error", path.name, {"message": str(exc)})
                    self.log_callback(f"Failed to process {path.name}: {exc}")
            time.sleep(self.config.poll_interval_seconds)

    def _is_stable(self, path: Path) -> bool:
        stat = path.stat()
        key = str(path.resolve())
        snapshot = (stat.st_size, stat.st_mtime)
        previous = self._stability_cache.get(key)
        self._stability_cache[key] = snapshot
        if previous != snapshot:
            return False
        return (time.time() - stat.st_mtime) >= self.config.stability_window_seconds

    def process_file(self, path: Path) -> ProcessResult | None:
        source_hash = file_sha256(path)
        if self.manifest.has_processed(source_hash):
            return None

        stem = slugify_filename(path.stem)
        raw_destination = unique_destination(self.config.raw_archive_path, stem, path.suffix)
        copy2(path, raw_destination)

        text = path.read_text(encoding="utf-8")
        converted = convert_transcript(text)

        emacs_destination = unique_destination(self.config.emacs_path, stem, ".el")
        latex_destination = unique_destination(self.config.latex_path, stem, ".tex")
        emacs_destination.write_text(converted.emacs_text, encoding="utf-8")
        latex_destination.write_text(converted.latex_text, encoding="utf-8")

        payload = {
            "source_path": str(path),
            "archived_path": str(raw_destination),
            "emacs_path": str(emacs_destination),
            "latex_path": str(latex_destination),
            "processed_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.manifest.record(source_hash, payload)
        self._log_event("processed", path.name, payload)
        self.log_callback(f"Processed {path.name}")
        return ProcessResult(
            source_path=path,
            archived_path=raw_destination,
            emacs_path=emacs_destination,
            latex_path=latex_destination,
        )

    def _log_event(self, event_type: str, filename: str, payload: dict[str, str]) -> None:
        log_path = self.config.logs_path / "events.jsonl"
        record = {
            "event": event_type,
            "filename": filename,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "payload": payload,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
