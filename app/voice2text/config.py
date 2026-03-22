from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


DESKTOP_PROJECT = Path.home() / "Desktop" / "Voice2Text_OnDesktop"
APP_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "Voice2Text_OnDesktop"
APP_LOGS_DIR = Path.home() / "Library" / "Logs" / "Voice2Text_OnDesktop"
DEFAULT_CONFIG_PATH = APP_SUPPORT_DIR / "settings.json"


@dataclass
class AppConfig:
    desktop_project_dir: str = str(DESKTOP_PROJECT)
    macwhisper_export_dir: str = str(DESKTOP_PROJECT / "macwhisper_exports")
    recordings_dir: str = str(DESKTOP_PROJECT / "recordings")
    incoming_dir: str = str(DESKTOP_PROJECT / "incoming_transcripts")
    raw_archive_dir: str = str(DESKTOP_PROJECT / "raw_archive")
    emacs_dir: str = str(DESKTOP_PROJECT / "emacs")
    latex_dir: str = str(DESKTOP_PROJECT / "latex")
    logs_dir: str = str(DESKTOP_PROJECT / "logs")
    poll_interval_seconds: float = 2.0
    stability_window_seconds: float = 2.0

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        config_path = path or DEFAULT_CONFIG_PATH
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return cls(**data)

        config = cls()
        config.save(config_path)
        return config

    def save(self, path: Path | None = None) -> None:
        config_path = path or DEFAULT_CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open("w", encoding="utf-8") as handle:
            json.dump(asdict(self), handle, indent=2)

    @property
    def app_support_path(self) -> Path:
        return APP_SUPPORT_DIR

    @property
    def app_logs_path(self) -> Path:
        return APP_LOGS_DIR

    @property
    def desktop_project_path(self) -> Path:
        return Path(self.desktop_project_dir)

    @property
    def macwhisper_export_path(self) -> Path:
        return Path(self.macwhisper_export_dir)

    @property
    def incoming_path(self) -> Path:
        return Path(self.incoming_dir)

    @property
    def recordings_path(self) -> Path:
        return Path(self.recordings_dir)

    @property
    def raw_archive_path(self) -> Path:
        return Path(self.raw_archive_dir)

    @property
    def emacs_path(self) -> Path:
        return Path(self.emacs_dir)

    @property
    def latex_path(self) -> Path:
        return Path(self.latex_dir)

    @property
    def logs_path(self) -> Path:
        return Path(self.logs_dir)

    def ensure_directories(self) -> None:
        self.app_support_path.mkdir(parents=True, exist_ok=True)
        self.app_logs_path.mkdir(parents=True, exist_ok=True)
        self.desktop_project_path.mkdir(parents=True, exist_ok=True)
        self.macwhisper_export_path.mkdir(parents=True, exist_ok=True)
        self.recordings_path.mkdir(parents=True, exist_ok=True)
        self.incoming_path.mkdir(parents=True, exist_ok=True)
        self.raw_archive_path.mkdir(parents=True, exist_ok=True)
        self.emacs_path.mkdir(parents=True, exist_ok=True)
        self.latex_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
