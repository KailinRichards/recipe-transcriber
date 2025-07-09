from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    video_id = str(uuid.uuid4())
    video_filename = f"video_{video_id}.mp4"

    try:
        subprocess.run(["yt-dlp", "-f", "best", "-o", video_filename, url], check=True)
        subprocess.run(["whisper", video_filename, "--model", "base", "--output_format", "txt"], check=True)

        transcript_file = video_filename.replace(".mp4", ".txt")
        with open(transcript_file, "r") as f:
            transcript = f.read()

        return jsonify({
            "title": video_filename,
            "duration": "unknown",
            "transcript": transcript
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_filename):
            os.remove(video_filename)
        transcript_txt = video_filename.replace(".mp4", ".txt")
        if os.path.exists(transcript_txt):
            os.remove(transcript_txt)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)