# Speech-to-Text Transcription Demo (Whisper)

A minimal web app: click a button, speak, and see your speech transcribed
using a locally-run OpenAI Whisper model.

**Note:** since this runs the microphone on the *server* (not the browser),
run it on your own machine — `python app.py` and open `localhost:5000` —
so "the server" and "your mic" are the same computer.

## Tech stack
- **SpeechRecognition** — captures audio from the microphone (via PyAudio) and hands it to the recognizer
- **PyAudio** — low-level microphone access
- **OpenAI Whisper** — the actual speech-to-text model
- **PyTorch** — runs the Whisper model
- **NumPy** — array/audio-buffer handling used internally by Whisper
- **FFmpeg** — decodes/resamples audio for Whisper (system dependency, not a Python package)
- **Flask** — tiny web server tying it all together
- Plain **HTML/CSS/JS** — the UI

## 1. Install system dependencies

**FFmpeg**
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
- Windows: download from https://ffmpeg.org/download.html and add it to your PATH

**PortAudio** (needed for PyAudio to build/install)
- macOS: `brew install portaudio`
- Ubuntu/Debian: `sudo apt install portaudio19-dev python3-pyaudio`
- Windows: usually installs fine via pip directly

## 2. Install Python dependencies

It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

If `pyaudio` fails to install on Windows, try:
```bash
pip install pipwin
pipwin install pyaudio
```

## 3. Run the app

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

Click **"Start Recording"**, speak a sentence, and the transcript will
appear in the text box below. The first request will be slower since
Whisper downloads and loads the model weights.

## Notes on accuracy vs. speed

In `app.py`, `WHISPER_MODEL` controls which Whisper model is loaded:

| Model  | Relative speed | Accuracy   |
|--------|-----------------|------------|
| tiny   | fastest         | lowest     |
| base   | fast            | good (default) |
| small  | moderate        | better     |
| medium | slow            | very good  |
| large  | slowest         | best       |

For a live demo on a laptop CPU, `base` or `small` is usually the sweet
spot. Switch to `small`/`medium` if you have a GPU or need higher accuracy
and don't mind the extra latency.

## How it works

1. Browser sends `POST /record` when you click the button.
2. Flask opens the microphone via `speech_recognition.Microphone()`
   (backed by PyAudio), calibrates for ambient noise, then records
   until you stop talking (or hits the time limit).
3. The captured audio is passed to `recognizer.recognize_whisper(...)`,
   which runs OpenAI's Whisper model locally through PyTorch to produce
   the transcript.
4. The transcript is returned as JSON and rendered in the page.
