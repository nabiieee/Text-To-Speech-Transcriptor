const btn = document.getElementById("recordBtn");
const clearBtn = document.getElementById("clearBtn");
const status = document.getElementById("status");
const transcriptBox = document.getElementById("transcript");

btn.addEventListener("click", async () => {
  btn.disabled = true;
  btn.textContent = "Listening...";
  status.textContent = "🎙️ Speak now...";
  status.className = "status listening";

  try {
    const res = await fetch("/record", { method: "POST" });
    const data = await res.json();

    if (data.success) {
      transcriptBox.value += (transcriptBox.value ? "\n" : "") + data.transcript;
      status.textContent = "✅ Transcribed successfully";
      status.className = "status success";
    } else {
      status.textContent = "⚠️ " + data.error;
      status.className = "status error";
    }
  } catch (err) {
    status.textContent = "❌ Could not reach the server.";
    status.className = "status error";
  } finally {
    btn.disabled = false;
    btn.textContent = "Start Recording";
  }
});

clearBtn.addEventListener("click", () => {
  transcriptBox.value = "";
  status.textContent = "";
  status.className = "status";
});
