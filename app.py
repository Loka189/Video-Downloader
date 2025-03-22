from flask import Flask, render_template, request, send_from_directory
import os
import yt_dlp
from urllib.parse import quote

app = Flask(__name__)

# Save the cookie from ENV to a file
COOKIE_FILE_PATH = 'youtube_cookies.txt'
cookie_content = os.environ.get("YOUTUBE_COOKIES", "")
if cookie_content:
    with open(COOKIE_FILE_PATH, 'w') as f:
        f.write(cookie_content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    download_path = 'downloads/%(title)s.%(ext)s'

    ydl_opts = {
        'outtmpl': download_path,
        'cookiefile': COOKIE_FILE_PATH if os.path.exists(COOKIE_FILE_PATH) else None,
        'verbose': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
    except Exception as e:
        return f"<h3>❌ Download Failed</h3><pre>{str(e)}</pre>"

    safe_filename = quote(os.path.basename(video_filename))
    return f"""
    <h2>✅ Download Completed</h2>
    <a href="/get_video/{safe_filename}">➡ Click here to download your video</a><br><br>
    <small>File saved as: {video_filename}</small>
    """

@app.route('/get_video/<path:filename>')
def get_video(filename):
    try:
        return send_from_directory('downloads', filename, as_attachment=True)
    except FileNotFoundError:
        return "❌ File not found!", 404


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
