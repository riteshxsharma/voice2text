from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from voice2text.config import AppConfig
from voice2text.session_control import DictationSessionController


class SessionControlApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Voice2Text Session Control")
        self.root.geometry("720x420")

        self.config = AppConfig.load()
        self.controller = DictationSessionController(self.config)

        self.session_label_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value=(
                "Press Start Session, record in MacWhisper, export the transcript to the configured "
                "MacWhisper folder, then press Stop Session."
            )
        )

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Session name").pack(anchor="w")
        ttk.Entry(frame, textvariable=self.session_label_var).pack(fill="x", pady=(4, 12))

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 12))
        ttk.Button(controls, text="Start Session", command=self.start_session).pack(side="left")
        ttk.Button(controls, text="Stop Session", command=self.stop_session).pack(side="left", padx=(8, 0))

        locations = (
            f"MacWhisper export folder: {self.config.macwhisper_export_path}\n"
            f"Incoming transcript folder: {self.config.incoming_path}\n"
            f"Desktop project folder: {self.config.desktop_project_path}"
        )
        ttk.Label(frame, text=locations, justify="left").pack(anchor="w", pady=(0, 12))

        ttk.Label(frame, textvariable=self.status_var, wraplength=680, justify="left").pack(anchor="w")

        self.log_box = tk.Text(frame, height=12, width=80)
        self.log_box.pack(fill="both", expand=True, pady=(12, 0))
        self._append_log("Session control ready.")

    def start_session(self) -> None:
        state = self.controller.start_session(self.session_label_var.get())
        self.status_var.set(f"Session active: {state.label}. Record in MacWhisper, then export the transcript.")
        self._append_log(f"Started session {state.label} at {state.started_at.isoformat(timespec='seconds')}")

    def stop_session(self) -> None:
        imported = self.controller.stop_session()
        if imported:
            self.status_var.set(f"Imported {len(imported)} transcript file(s) into the processing queue.")
            for item in imported:
                self._append_log(f"Imported {item.name}")
        else:
            self.status_var.set("No new MacWhisper transcript files were found for the active session.")
            self._append_log("Stopped session with no matching exports found.")

    def _append_log(self, message: str) -> None:
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")


def main() -> None:
    root = tk.Tk()
    SessionControlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
