# Voice2Text_OnDesktop

A local Python desktop prototype for low-friction technical dictation on macOS.

Primary entrypoint:

- `desktop_app.py` combines recording, session management, transcript queueing, processing, preview, and settings in one app.

Legacy entrypoints are still available:

- `session_control_app.py`
- `background_processor_app.py`

## Workflow

1. Launch the unified desktop app.
2. Press `Start Recording`.
3. Speak into the microphone. The app saves a `.wav` recording locally.
4. Stop recording.
5. Transcribe that recording in MacWhisper and export the transcript `.txt` file into the configured MacWhisper export folder.
6. Click `Import MacWhisper Exports Now` if the transcript was exported after the session ended.
7. The built-in processor archives the raw transcript and writes Emacs and LaTeX outputs.
8. Use the Recent Outputs and Preview panes to inspect the results.

## Important scope note

This prototype records audio directly with `rec` from SoX, but it still does not click buttons inside MacWhisper or control macOS Dictation directly. Transcription remains external unless you install a local transcription backend later. That keeps the implementation aligned with the original MacWhisper-first MVP while reducing friction.

## Run

Use Python 3.11+ and set `PYTHONPATH=app`.

```bash
PYTHONPATH=app python3 app/desktop_app.py
```

## Icon Assets

The repo includes high-contrast icon assets aimed at low-vision usability:

- `/Users/lrram/Documents/Projects/voice2text/assets/icons/voice2text_on.png`
- `/Users/lrram/Documents/Projects/voice2text/assets/icons/voice2text_off.png`
- `/Users/lrram/Documents/Projects/voice2text/assets/icons/voice2text_on.svg`
- `/Users/lrram/Documents/Projects/voice2text/assets/icons/voice2text_off.svg`

Regenerate them with:

```bash
python3 /Users/lrram/Documents/Projects/voice2text/assets/icons/generate_icons.py
```

## macOS App Bundles

Build Dock-launchable apps with:

```bash
python3 /Users/lrram/Documents/Projects/voice2text/scripts/build_macos_apps.py
```

That creates:

- `/Users/lrram/Documents/Projects/voice2text/dist/Voice2Text On.app`
- `/Users/lrram/Documents/Projects/voice2text/dist/Voice2Text Off.app`

`Voice2Text On.app` launches the unified desktop app.

`Voice2Text Off.app` stops it.

## Desktop output

By default the apps create and use:

- `/Users/lrram/Desktop/Voice2Text_OnDesktop/macwhisper_exports`
- `/Users/lrram/Desktop/Voice2Text_OnDesktop/recordings`
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
