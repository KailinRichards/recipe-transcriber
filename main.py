from flask import Flask, request, jsonify
import yt_dlp
import whisper
import os
import uuid

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Recipe Transcriber is live!"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    # Use a unique filename
    video_id = str(uuid.uuid4())
    video_filename = f"{video_id}.mp4"

    try:
        # Download video using yt_dlp
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': video_filename,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Load Whisper model and transcribe
        model = whisper.load_model("base")
        result = model.transcribe(video_filename)

        return jsonify({
            "transcript": result["text"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(video_filename):
            os.remove(video_filename)

# Make sure it runs on Render’s assigned port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
