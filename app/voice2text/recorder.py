from __future__ import annotations

import shutil
import signal
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import AppConfig
from .storage import slugify_filename, unique_destination


@dataclass
class RecordingState:
    output_path: Path
    started_at: datetime


class AudioRecorder:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.config.ensure_directories()
        self._process: subprocess.Popen[str] | None = None
        self._state: RecordingState | None = None

    @property
    def is_recording(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def current_state(self) -> RecordingState | None:
        return self._state

    def start(self, label: str = "") -> RecordingState:
        if self.is_recording:
            return self._state  # type: ignore[return-value]

        if shutil.which("rec") is None:
            raise RuntimeError("The 'rec' command is not available. Install SoX to enable recording.")

        stem = slugify_filename(label) if label.strip() else datetime.now().strftime("session_%Y%m%d_%H%M%S")
        output_path = unique_destination(self.config.recordings_path, stem, ".wav")
        command = [
            "rec",
            "-q",
            str(output_path),
            "rate",
            "16000",
            "channels",
            "1",
        ]
        self._process = subprocess.Popen(command)
        self._state = RecordingState(output_path=output_path, started_at=datetime.now())
        return self._state

    def stop(self) -> Path | None:
        if not self.is_recording or self._process is None:
            self._state = None
            return None

        self._process.send_signal(signal.SIGINT)
        self._process.wait(timeout=10)
        output_path = self._state.output_path if self._state else None
        self._process = None
        self._state = None
        return output_path
