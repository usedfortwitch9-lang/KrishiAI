from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from backend import ask_gemini
import socket
import qrcode
import os

app = Flask(__name__, static_folder="frontend")
CORS(app)


def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def generate_qr_code(url):
    """Generate QR code"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = "qr_code.png"
    img.save(qr_path)
    print(f"\n✅ QR Code saved: {qr_path}")
    return qr_path


# Serve website
@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("frontend", path)


# CHATBOT API - THIS IS THE IMPORTANT ONE
@app.route("/chat", methods=["POST"])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        user_msg = data.get("message", "").strip()

        if not user_msg:
            return jsonify({"error": "Empty message"}), 400

        print(f"\n💬 User: {user_msg}")

        # Get reply from Gemini
        reply = ask_gemini(user_msg)

        print(f"🤖 Bot: {reply[:100]}...\n")

        # IMPORTANT: Return in correct format
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"❌ Server error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/test")
def test():
    """Test endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Server is running!"
    })


if __name__ == "__main__":
    port = 8000
    local_ip = get_local_ip()

    local_url = f"http://{local_ip}:{port}"
    localhost_url = f"http://localhost:{port}"

    print("\n" + "=" * 60)
    print("🚀 KANNADA AI CHATBOT SERVER")
    print("=" * 60)
    print(f"\n📱 LOCAL: {localhost_url}")
    print(f"🌐 NETWORK: {local_url}")
    print(f"\n📶 IP: {local_ip}")

    # Generate QR
    print(f"\n🔲 Generating QR code...")
    qr_path = generate_qr_code(local_url)

    print(f"\n📸 Scan {qr_path} to access from phone")
    print("\n💡 Make sure all devices are on same WiFi!")
    print("=" * 60 + "\n")

    # Start server
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        ssl_context=("cert.pem", "key.pem")
    )
