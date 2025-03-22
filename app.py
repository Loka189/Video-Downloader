import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    video_id = extract_video_id(url)

    piped_api = f"https://pipedapi.kavin.rocks/streams/{video_id}"
    res = requests.get(piped_api)

    if res.status_code != 200:
        return "❌ Failed to fetch video from Piped API"

    data = res.json()
    title = data.get("title", "video")

    # Get best quality video stream
    video_stream = data['videoStreams'][0]
    video_url = video_stream['url']
    quality = video_stream['quality']
    format_ = video_stream['format']

    return f"""
    <h2>✅ Video Found: {title}</h2>
    <p>Best Quality: {quality} ({format_})</p>
    <a href="{video_url}" download="{title}.{format_}">➡ Click here to download</a><br>
    """

def extract_video_id(url):
    # Basic parser for YouTube video ID
    import re
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

