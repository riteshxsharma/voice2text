from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from shutil import copy2

from .config import AppConfig
from .storage import slugify_filename, unique_destination


@dataclass
class SessionState:
    started_at: datetime | None = None
    label: str = ""
    recording_path: Path | None = None

    @property
    def is_active(self) -> bool:
        return self.started_at is not None


class DictationSessionController:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.config.ensure_directories()
        self.state = SessionState()
        self._last_session = SessionState()
        self._imported_exports: set[str] = set()

    def start_session(self, label: str = "", recording_path: Path | None = None) -> SessionState:
        if self.state.is_active:
            return self.state
        cleaned = slugify_filename(label) if label.strip() else datetime.now().strftime("session_%Y%m%d_%H%M%S")
        self.state = SessionState(started_at=datetime.now(), label=cleaned, recording_path=recording_path)
        return self.state

    def stop_session(self) -> list[Path]:
        if not self.state.is_active or not self.state.started_at:
            return []

        imported = self._import_exports_for_session(self.state)
        self._last_session = self.state
        self.state = SessionState()
        return imported

    def import_last_session_exports(self) -> list[Path]:
        session = self.state if self.state.is_active else self._last_session
        if not session.is_active or not session.started_at:
            return []

        return self._import_exports_for_session(session)

    def _import_exports_for_session(self, session: SessionState) -> list[Path]:
        imported: list[Path] = []
        for export_path in sorted(self.config.macwhisper_export_path.glob("*.txt")):
            resolved = str(export_path.resolve())
            if resolved in self._imported_exports:
                continue
            modified_at = datetime.fromtimestamp(export_path.stat().st_mtime)
            if modified_at < session.started_at:
                continue
            stem = f"{session.label}_{slugify_filename(export_path.stem)}"
            destination = unique_destination(self.config.incoming_path, stem, export_path.suffix)
            copy2(export_path, destination)
            imported.append(destination)
            self._imported_exports.add(resolved)
        return imported
