from flask import Flask, request, jsonify
import subprocess
import os
import uuid
from PyPDF2 import PdfReader  # <- NEW
from flask_cors import CORS  # <- For CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Try JSON payload for URL
    data = request.get_json(silent=True)
    url = data.get("url") if data else None

    # Handle PDF file upload
    if 'file' in request.files:
        pdf = request.files['file']
        try:
            reader = PdfReader(pdf)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return jsonify({
                "title": pdf.filename,
                "duration": "n/a",
                "transcript": text
            })
        except Exception as e:
            return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500

    # Error if no URL or PDF provided
    if not url:
        return jsonify({"error": "Missing URL or file"}), 400

    # Download and transcribe video
    video_id = str(uuid.uuid4())
    video_filename = f"video_{video_id}.mp4"

    try:
        subprocess.run(["yt-dlp", "-f", "best", "-o", video_filename, url], check=True)
        subprocess.run(["whisper", video_filename, "--model", "base", "--output_format", "txt"], check=True)

        transcript_file = video_filename.replace(".mp4", ".txt")

        if not os.path.exists(transcript_file):
            raise FileNotFoundError(f"Transcript file {transcript_file} not found")

        with open(transcript_file, "r") as f:
            transcript = f.read()

        return jsonify({
            "title": video_filename,
            "duration": "unknown",
            "transcript": transcript
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Subprocess failed: {str(e)}"}), 500
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    finally:
    if os.path.exists(video_filename):
        os.remove(video_filename)

    transcript_txt = video_filename.replace(".mp4", ".txt")
    if os.path.exists(transcript_txt):
        os.remove(transcript_txt)
