"""
Speech-to-Text Transcription Demo
----------------------------------
Backend stack: SpeechRecognition (mic capture via PyAudio) + OpenAI Whisper
(running on PyTorch/NumPy) for the actual transcription. FFmpeg is used
under the hood by Whisper to decode/resample the captured audio.

Flow:
  1. Browser hits POST /record
  2. Server opens the microphone (PyAudio, wrapped by SpeechRecognition)
  3. Captures a phrase, hands the audio to Whisper for transcription
  4. Returns the transcribed text as JSON
"""

from flask import Flask, render_template, jsonify
import speech_recognition as sr

app = Flask(__name__)

# Recognizer instance is created once and reused across requests.
recognizer = sr.Recognizer()

# Whisper model size: tiny / base / small / medium / large
# Bigger = more accurate but slower and more memory-hungry.
# "base" is a good balance for a demo running on CPU.
WHISPER_MODEL = "base"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/record", methods=["POST"])
def record():
    try:
        with sr.Microphone() as source:
            # Calibrate for background noise for half a second before listening.
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Wait up to 5s for speech to start, then capture up to 15s of speech.
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=30)

        # recognize_whisper runs OpenAI Whisper locally (via PyTorch).
        # No internet call is made once the model weights are downloaded/cached.
        text = recognizer.recognize_whisper(
            audio,
            model=WHISPER_MODEL,
            language="english",
        )

        return jsonify({"success": True, "transcript": text.strip()})

    except sr.WaitTimeoutError:
        return jsonify({"success": False, "error": "No speech detected — timed out waiting for you to start talking."})
    except sr.UnknownValueError:
        return jsonify({"success": False, "error": "Could not understand the audio. Try speaking more clearly."})
    except OSError as e:
        return jsonify({"success": False, "error": f"Microphone error: {e}. Is a mic connected and accessible?"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    # Loading the Whisper model can take a few seconds on first request
    # (and the first-ever run will download the model weights).
    app.run(debug=True, port=5000)
