from __future__ import annotations

import queue
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from voice2text.config import AppConfig
from voice2text.processor import TranscriptProcessor
from voice2text.recorder import AudioRecorder
from voice2text.session_control import DictationSessionController
from voice2text.storage import slugify_filename, unique_destination


class Voice2TextDesktopApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Voice2Text OnDesktop")
        self.root.geometry("1100x760")
        self.root.configure(bg="#f3f6f4")

        self.config = AppConfig.load()
        self.config.ensure_directories()
        self.ui_queue: queue.SimpleQueue[tuple[str, str]] = queue.SimpleQueue()
        self.processor = TranscriptProcessor(self.config, log_callback=self._queue_log)
        self.recorder = AudioRecorder(self.config)
        self.session_controller = DictationSessionController(self.config)

        self.session_name_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready.")
        self.macwhisper_dir_var = tk.StringVar(value=str(self.config.macwhisper_export_path))
        self.selected_result: dict[str, str] | None = None

        self._build_ui()
        self.processor.start()
        self.refresh_recent_outputs()
        self._append_log("Unified app ready. Background processor is running.")
        self.root.after(150, self._present_window)
        self.root.after(400, self._drain_ui_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x")

        left = ttk.Frame(top)
        left.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Session name").pack(anchor="w")
        ttk.Entry(left, textvariable=self.session_name_var).pack(fill="x", pady=(4, 12))

        buttons = ttk.Frame(left)
        buttons.pack(fill="x", pady=(0, 12))
        ttk.Button(buttons, text="Start Recording", command=self.start_recording).pack(side="left")
        ttk.Button(buttons, text="Stop Recording + Import", command=self.stop_recording).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="Import MacWhisper Exports Now", command=self.import_exports_now).pack(side="left", padx=(8, 0))

        settings = ttk.LabelFrame(left, text="Folders", padding=12)
        settings.pack(fill="x")
        ttk.Label(settings, text="MacWhisper transcript export folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings, textvariable=self.macwhisper_dir_var).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        ttk.Button(settings, text="Browse", command=self.choose_macwhisper_folder).grid(row=1, column=1, padx=(8, 0))
        ttk.Button(settings, text="Save", command=self.save_settings).grid(row=1, column=2, padx=(8, 0))
        settings.columnconfigure(0, weight=1)

        ttk.Label(
            left,
            text=(
                f"Recordings: {self.config.recordings_path}\n"
                f"Incoming: {self.config.incoming_path}\n"
                f"Emacs output: {self.config.emacs_path}\n"
                f"LaTeX output: {self.config.latex_path}"
            ),
            justify="left",
        ).pack(anchor="w", pady=(12, 0))

        right = ttk.LabelFrame(top, text="Manual Transcript", padding=12)
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))
        ttk.Label(
            right,
            text="Paste transcript text here if you want to bypass MacWhisper for a quick test.",
            wraplength=380,
            justify="left",
        ).pack(anchor="w")
        self.manual_text = tk.Text(right, height=12, width=45)
        self.manual_text.pack(fill="both", expand=True, pady=(8, 8))
        ttk.Button(right, text="Save Manual Transcript To Queue", command=self.save_manual_transcript).pack(anchor="w")

        middle = ttk.Panedwindow(frame, orient="horizontal")
        middle.pack(fill="both", expand=True, pady=(16, 0))

        recent_frame = ttk.LabelFrame(middle, text="Recent Outputs", padding=12)
        preview_frame = ttk.LabelFrame(middle, text="Preview", padding=12)
        middle.add(recent_frame, weight=1)
        middle.add(preview_frame, weight=2)

        self.results_list = tk.Listbox(recent_frame, height=16)
        self.results_list.pack(fill="both", expand=True)
        self.results_list.bind("<<ListboxSelect>>", self.on_select_result)
        ttk.Button(recent_frame, text="Refresh", command=self.refresh_recent_outputs).pack(anchor="w", pady=(8, 0))

        preview_controls = ttk.Frame(preview_frame)
        preview_controls.pack(fill="x")
        ttk.Button(preview_controls, text="Show Emacs", command=lambda: self.show_preview("emacs_path")).pack(side="left")
        ttk.Button(preview_controls, text="Show LaTeX", command=lambda: self.show_preview("latex_path")).pack(side="left", padx=(8, 0))
        ttk.Button(preview_controls, text="Show Raw", command=lambda: self.show_preview("archived_path")).pack(side="left", padx=(8, 0))
        self.preview = tk.Text(preview_frame, height=18)
        self.preview.pack(fill="both", expand=True, pady=(8, 0))

        accessibility = tk.LabelFrame(
            frame,
            text="Large Workflow Buttons",
            font=("Helvetica", 18, "bold"),
            bg="#fff7db",
            fg="#1d2a1f",
            padx=16,
            pady=14,
            bd=3,
            relief="groove",
        )
        accessibility.pack(fill="x", pady=(16, 0))
        tk.Label(
            accessibility,
            text="Large duplicate buttons for the main workflow. Use these for quick access.",
            font=("Helvetica", 14, "bold"),
            bg="#fff7db",
            fg="#1d2a1f",
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        big_controls = tk.Frame(accessibility, bg="#fff7db")
        big_controls.pack(fill="x")
        self._build_large_button(
            big_controls,
            text="START RECORDING",
            command=self.start_recording,
            bg="#6f3fd1",
            active_bg="#5f31bf",
        ).pack(side="left", fill="x", expand=True)
        self._build_large_button(
            big_controls,
            text="STOP RECORDING",
            command=self.stop_recording,
            bg="#c9372c",
            active_bg="#ae2b21",
        ).pack(side="left", fill="x", expand=True, padx=18)
        self._build_large_button(
            big_controls,
            text="PROCESS",
            command=self.import_exports_now,
            bg="#1f9d55",
            active_bg="#177a41",
        ).pack(side="left", fill="x", expand=True)

        bottom = ttk.LabelFrame(frame, text="Status", padding=12)
        bottom.pack(fill="both", expand=False, pady=(16, 0))
        ttk.Label(bottom, textvariable=self.status_var, wraplength=1050, justify="left").pack(anchor="w")
        self.log_box = tk.Text(bottom, height=10)
        self.log_box.pack(fill="both", expand=True, pady=(8, 0))

    def start_recording(self) -> None:
        try:
            recording = self.recorder.start(self.session_name_var.get())
            session = self.session_controller.start_session(self.session_name_var.get(), recording.output_path)
        except Exception as exc:
            self.status_var.set(f"Failed to start recording: {exc}")
            self._append_log(f"Failed to start recording: {exc}")
            return

        self.status_var.set(
            f"Recording started: {recording.output_path.name}. When finished, stop recording, then transcribe the WAV in MacWhisper."
        )
        self._append_log(f"Recording to {recording.output_path}")
        self._append_log(f"Session active: {session.label}")

    def stop_recording(self) -> None:
        audio_path = self.recorder.stop()
        imported = self.session_controller.stop_session()
        if audio_path:
            self._append_log(f"Stopped recording: {audio_path}")
        if imported:
            self.status_var.set(f"Imported {len(imported)} transcript file(s). Background processing will pick them up automatically.")
            for path in imported:
                self._append_log(f"Queued transcript: {path.name}")
        else:
            self.status_var.set(
                "Recording stopped. No new MacWhisper transcripts were found yet. Transcribe the WAV in MacWhisper, export the .txt, then click 'Import MacWhisper Exports Now'."
            )
        self.refresh_recent_outputs()

    def import_exports_now(self) -> None:
        imported = self.session_controller.import_last_session_exports()
        if imported:
            self.status_var.set(f"Imported {len(imported)} transcript file(s) into the queue.")
            for path in imported:
                self._append_log(f"Queued transcript: {path.name}")
        else:
            self.status_var.set("No new MacWhisper transcript exports matched the last session.")
        self.refresh_recent_outputs()

    def choose_macwhisper_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=str(self.config.macwhisper_export_path))
        if selected:
            self.macwhisper_dir_var.set(selected)

    def save_settings(self) -> None:
        self.config.macwhisper_export_dir = self.macwhisper_dir_var.get().strip()
        self.config.ensure_directories()
        self.config.save()
        self.status_var.set("Settings saved.")
        self._append_log(f"Saved MacWhisper folder: {self.config.macwhisper_export_path}")

    def save_manual_transcript(self) -> None:
        text = self.manual_text.get("1.0", "end").strip()
        if not text:
            self.status_var.set("Manual transcript box is empty.")
            return

        stem = slugify_filename(self.session_name_var.get()) if self.session_name_var.get().strip() else "manual_transcript"
        destination = unique_destination(self.config.incoming_path, stem, ".txt")

        destination.write_text(text + "\n", encoding="utf-8")
        self.status_var.set(f"Saved manual transcript to queue: {destination.name}")
        self._append_log(f"Manual transcript queued: {destination}")
        self.manual_text.delete("1.0", "end")

    def refresh_recent_outputs(self) -> None:
        self.results = self.processor.recent_results(limit=20)
        self.results_list.delete(0, "end")
        for record in self.results:
            timestamp = record.get("timestamp", "")
            filename = record.get("filename", "")
            self.results_list.insert("end", f"{timestamp}  {filename}")

    def on_select_result(self, _event: object) -> None:
        selection = self.results_list.curselection()
        if not selection:
            return
        self.selected_result = self.results[selection[0]]
        self.show_preview("latex_path")

    def show_preview(self, key: str) -> None:
        if not self.selected_result:
            return
        payload = self.selected_result.get("payload", {})
        path_value = payload.get(key)
        if not path_value:
            return
        path = Path(path_value)
        if not path.exists():
            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", f"Missing file: {path}")
            return
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", path.read_text(encoding="utf-8"))

    def _append_log(self, message: str) -> None:
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")

    def _build_large_button(
        self,
        parent: tk.Widget,
        *,
        text: str,
        command: object,
        bg: str,
        active_bg: str,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Helvetica", 20, "bold"),
            bg=bg,
            fg="white",
            activebackground=active_bg,
            activeforeground="white",
            relief="raised",
            bd=5,
            padx=18,
            pady=20,
            cursor="hand2",
            highlightthickness=2,
            highlightbackground="#ffffff",
            highlightcolor="#ffffff",
        )

    def _present_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(500, lambda: self.root.attributes("-topmost", False))

    def _queue_log(self, message: str) -> None:
        self.ui_queue.put(("log", message))

    def _drain_ui_queue(self) -> None:
        while True:
            try:
                event_type, payload = self.ui_queue.get_nowait()
            except queue.Empty:
                break

            if event_type == "log":
                self._append_log(payload)
                self.refresh_recent_outputs()

        self.root.after(400, self._drain_ui_queue)

    def _on_close(self) -> None:
        if self.recorder.is_recording:
            self.recorder.stop()
        self.processor.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    Voice2TextDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
