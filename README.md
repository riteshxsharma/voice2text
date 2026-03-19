# Voice2Text_OnDesktop

Two local Python apps for a MacWhisper-first dictation workflow:

- `session_control_app.py` starts and stops a dictation session.
- `background_processor_app.py` watches transcript files and generates `.el` and `.tex` outputs.

## Workflow

1. Launch the session control app.
2. Press `Start Session`.
3. Record and transcribe in MacWhisper.
4. Export the transcript `.txt` file into the configured MacWhisper export folder.
5. Press `Stop Session`.
6. Launch or keep running the background processor app.
7. The processor archives the raw transcript and writes Emacs and LaTeX outputs.

## Important scope note

This prototype does not click buttons inside MacWhisper or control macOS Dictation directly. The session app wraps the workflow with a start/stop button and imports transcripts created during that session. That keeps the implementation aligned with the original MacWhisper-first MVP and avoids brittle UI automation.

## Run

Use Python 3.11+ and set `PYTHONPATH=app`.

```bash
PYTHONPATH=app python3 app/session_control_app.py
PYTHONPATH=app python3 app/background_processor_app.py
```

## Desktop output

By default the apps create and use:

- `/Users/lrram/Desktop/Voice2Text_OnDesktop/macwhisper_exports`
- `/Users/lrram/Desktop/Voice2Text_OnDesktop/incoming_transcripts`
- `/Users/lrram/Desktop/Voice2Text_OnDesktop/raw_archive`
- `/Users/lrram/Desktop/Voice2Text_OnDesktop/emacs`
- `/Users/lrram/Desktop/Voice2Text_OnDesktop/latex`
- `/Users/lrram/Desktop/Voice2Text_OnDesktop/logs`

## Current grammar

The v1 conversion layer supports a small deterministic grammar:

- `begin equation` / `end equation`
- `alpha`, `beta`, `gamma`, `pi`
- `equals`
- `over`
- `slash`
- `open parenthesis`, `close parenthesis`
- `open brace`, `close brace`
- `new line`
