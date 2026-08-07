# Speech-to-Text Transcription Demo (Whisper)

A small web app: click a button, speak into your browser's microphone, and
see your speech transcribed using OpenAI Whisper — running locally, no
cloud API calls.

## Tech stack
- **OpenAI Whisper** — the actual speech-to-text model
- **PyTorch** — runs the Whisper model
- **NumPy** — array/audio-buffer handling used internally by Whisper
- **FFmpeg** — decodes the audio Whisper receives (system dependency)
- **Flask** — tiny Python web server tying it all together
- **MediaRecorder API** (browser JS) — captures audio from your microphone
- Plain **HTML/CSS/JS** — the UI

## How it works

1. Click **Start Recording** — your browser asks for microphone permission
   and starts recording using the `MediaRecorder` API.
2. Click **Stop Recording** — the clip is uploaded to the Flask backend.
3. Flask saves it to a temp file and passes it to Whisper
   (`model.transcribe(...)`), which runs locally via PyTorch.
4. The transcript comes back as JSON and is displayed on the page.

## Getting started (run it on your own machine)

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd speech-to-text-app
```

### 2. Install FFmpeg (system dependency, not a Python package)

- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
- **Windows:** download from https://ffmpeg.org/download.html and add it to your PATH

### 3. Set up a virtual environment and install Python dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

> First install downloads PyTorch + Whisper, which can take a few minutes
> depending on your connection.

### 4. Run the app

```bash
python app.py
```

Open **http://localhost:5000** in your browser. Click **Start Recording**,
allow microphone access when prompted, speak a sentence, then click
**Stop Recording** — your transcript will appear a few seconds later.

> The very first transcription will be slower than the rest, since Whisper
> downloads its model weights (~140MB for the default `base` model) the
> first time it runs, then caches them locally.

## Tuning accuracy vs. speed

`WHISPER_MODEL` near the top of `app.py` controls which Whisper model size
is used (also overridable via a `WHISPER_MODEL` environment variable):

| Model  | Relative speed | Accuracy   | Rough RAM needed |
|--------|-----------------|------------|-------------------|
| tiny   | fastest         | lowest     | ~1GB |
| base   | fast            | good (default) | ~1GB |
| small  | moderate        | better     | ~2GB |
| medium | slow            | very good  | ~5GB |
| large  | slowest         | best       | ~10GB |

If your machine has decent RAM/CPU (or a GPU), bumping this up to `small`
or `medium` noticeably improves accuracy on short phrases and names.

Other tunables worth knowing about, set where `model.transcribe(...)` is
called in `app.py`:
- `condition_on_previous_text=False` — reduces Whisper carrying earlier
  mistakes forward into later words
- `initial_prompt` — gives the model a little context, which helps on
  short, casual phrases
- `temperature=0.0` — deterministic decoding instead of sampling

## Notes / known limitations

- This runs Whisper **locally on your CPU** by default — no cloud calls,
  no API key needed, but transcription speed depends on your hardware.
- Microphone access requires either `localhost` or HTTPS — this is a
  browser security requirement (`getUserMedia`), so it works out of the
  box locally but would need HTTPS if ever deployed publicly.
- Not currently hosted anywhere public — this is set up for local/dev use.
  If you'd like to deploy it, the code is already structured for that (see
  below) — just needs a host like Render or Railway that supports
  long-running Python processes (Vercel-style serverless won't work here
  due to PyTorch/Whisper's size and runtime).

<details>
<summary>Optional: deploying this publicly later</summary>

The repo includes a `render.yaml` for deploying to [Render](https://render.com)
as a normal web service:

1. Push the repo to GitHub
2. On Render: **New +** → **Web Service** → select the repo
3. Render auto-detects `render.yaml` and deploys with `WHISPER_MODEL=base`
   (kept small to fit free-tier RAM limits)
4. You'll get a public HTTPS URL once it's live

Free-tier instances spin down when idle and take ~30–60s to wake up on the
next visit — normal for free hosting.
</details>
