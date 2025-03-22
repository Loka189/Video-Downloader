from flask import Flask, request, render_template, send_file
import os
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']

    # Extract video ID from URL
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return "❌ Invalid YouTube URL!"

    try:
        # Fetch video info from Piped API
        piped_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
        response = requests.get(piped_url)
        if response.status_code != 200:
            return "❌ Failed to fetch video from Piped API"

        data = response.json()
        if 'videoStreams' not in data or len(data['videoStreams']) == 0:
            return "❌ No video streams found"

        # Select best quality stream
        stream_url = data['videoStreams'][0]['url']

        # Download video stream
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        output_path = f'downloads/{video_id}.mp4'
        video_content = requests.get(stream_url, stream=True)
        with open(output_path, 'wb') as f:
            for chunk in video_content.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)

        return f"""
        <h2>✅ Download Complete</h2>
        <a href="/get_video/{video_id}.mp4">Download Your Video</a>
        """
    except Exception as e:
        return f"❌ Something went wrong: {e}"

@app.route('/get_video/<filename>')
def get_video(filename):
    try:
        return send_file(f"downloads/{filename}", as_attachment=True)
    except FileNotFoundError:
        return "❌ File not found!"

def extract_youtube_video_id(url):
    try:
        query = urlparse(url)
        if query.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(query.query).get('v', [None])[0]
        elif query.hostname == 'youtu.be':
            return query.path[1:]
    except Exception:
        return None

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
