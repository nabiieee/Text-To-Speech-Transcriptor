"""
Speech-to-Text Transcription Demo — faster-whisper version
-------------------------------------------------------------
Same mic-capture flow as app.py (SpeechRecognition + PyAudio), but
transcription runs through `faster-whisper` instead of `openai-whisper`.

faster-whisper reimplements Whisper using CTranslate2, a fast inference
engine for transformer models. Same underlying model weights and accuracy
per model size as openai-whisper, but typically 2-4x faster on CPU, and
supports int8 quantization for a further speed boost with only a small
accuracy trade-off.

Flow:
  1. Browser hits POST /record
  2. Server opens the microphone (PyAudio, wrapped by SpeechRecognition)
  3. Captures a phrase as WAV bytes, hands them to faster-whisper directly
     (no temp file needed — faster-whisper can read from an in-memory
     BytesIO stream)
  4. Returns the transcribed text as JSON
"""

import io

from flask import Flask, render_template, jsonify
import speech_recognition as sr
from faster_whisper import WhisperModel

app = Flask(__name__)

# Recognizer instance is created once and reused across requests.
recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.5

# Fixed energy threshold instead of adjust_for_ambient_noise() — removes
# the calibration delay before listening starts. Tune this number for your
# room/mic if it's too sensitive or not sensitive enough.
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 300

# Whisper model size: tiny / base / small / medium / large-v2 / large-v3
WHISPER_MODEL = "small"

# device: "cpu" or "cuda" (if you have an NVIDIA GPU + CUDA installed)
# compute_type: precision/quantization used for inference.
#   - "int8"     -> fastest on CPU, small accuracy trade-off (recommended default here)
#   - "int8_float16" -> good speed/accuracy balance on GPU
#   - "float16"  -> GPU only, more accurate than int8, still fast
#   - "float32"  -> most accurate, slowest — CPU or GPU
DEVICE = "cpu"
COMPUTE_TYPE = "int8"

# Model is loaded once at startup and reused across requests — loading it
# fresh per request would erase most of the speed benefit.
print(f"Loading faster-whisper model '{WHISPER_MODEL}' ({DEVICE}, {COMPUTE_TYPE})...")
model = WhisperModel(WHISPER_MODEL, device=DEVICE, compute_type=COMPUTE_TYPE)
print("Model loaded.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/record", methods=["POST"])
def record():
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=30)

        # Convert the captured audio to WAV bytes and hand it to
        # faster-whisper as an in-memory stream — no temp file needed.
        wav_bytes = io.BytesIO(audio.get_wav_data())

        segments, info = model.transcribe(
            wav_bytes,
            language="en",
            condition_on_previous_text=False,
            initial_prompt="This is a casual, conversational sentence spoken by one person.",
            temperature=0.0,
            beam_size=5,
        )

        # transcribe() returns a generator of segments — join them into
        # one string. This also means transcription happens lazily as we
        # iterate, so the "work" actually occurs on this line.
        text = " ".join(segment.text.strip() for segment in segments).strip()

        if not text:
            return jsonify({"success": False, "error": "Could not detect any speech in the recording."})

        return jsonify({"success": True, "transcript": text})

    except sr.WaitTimeoutError:
        return jsonify({"success": False, "error": "No speech detected — timed out waiting for you to start talking."})
    except OSError as e:
        return jsonify({"success": False, "error": f"Microphone error: {e}. Is a mic connected and accessible?"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
