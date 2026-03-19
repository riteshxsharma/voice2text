from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from voice2text.config import AppConfig
from voice2text.processor import TranscriptProcessor


class BackgroundProcessorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Voice2Text Background Processor")
        self.root.geometry("760x460")

        self.config = AppConfig.load()
        self.processor = TranscriptProcessor(self.config, log_callback=self._append_log)

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Background transcript processor").pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                f"Watching: {self.config.incoming_path}\n"
                f"Writing Emacs output: {self.config.emacs_path}\n"
                f"Writing LaTeX output: {self.config.latex_path}"
            ),
            justify="left",
        ).pack(anchor="w", pady=(4, 12))

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 12))
        ttk.Button(controls, text="Start Processor", command=self.processor.start).pack(side="left")
        ttk.Button(controls, text="Stop Processor", command=self.processor.stop).pack(side="left", padx=(8, 0))

        self.log_box = tk.Text(frame, height=18, width=90)
        self.log_box.pack(fill="both", expand=True)
        self._append_log("Processor UI ready.")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _append_log(self, message: str) -> None:
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")

    def _on_close(self) -> None:
        self.processor.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    BackgroundProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
