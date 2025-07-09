from flask import Flask, request, jsonify
from transcribe_utils import process_video  # this must be defined

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing 'url' in request"}), 400

    try:
        transcript = process_video(url)
        return jsonify({"transcript": transcript})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
