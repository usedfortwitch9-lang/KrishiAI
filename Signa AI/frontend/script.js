const input = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("messages");
const micBtn = document.getElementById("micBtn");

function addMessage(text, who) {
    const div = document.createElement("div");
    div.className = who === "user" ? "bubble user" : "bubble bot";
    div.innerText = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
    let msg = input.value.trim();
    if (!msg) return;
    addMessage(msg, "user");
    input.value = "";

    const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
    });

    const data = await res.json();

    addMessage(data.text, "bot");

    // PLAY AUDIO
    if (data.audio) {
        const audio = new Audio("data:audio/wav;base64," + data.audio);
        audio.play();
    }
}

sendBtn.onclick = sendMessage;
input.onkeypress = (e) => { if (e.key === "Enter") sendMessage(); };

// VOICE INPUT
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SR();
    rec.lang = "kn-IN";

    micBtn.onclick = () => rec.start();
    rec.onresult = (e) => {
        input.value = e.results[0][0].transcript;
        sendMessage();
    };
} else {
    micBtn.disabled = true;
}
