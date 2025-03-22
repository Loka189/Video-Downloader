from flask import Flask, render_template, request, send_from_directory
import os
import yt_dlp
from urllib.parse import quote


print("FILES IN DIR:", os.listdir())  # <- this will show in Railway logs

app = Flask(__name__)

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Download Handler
@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    download_path = 'downloads/%(title)s.%(ext)s'

    # Save the cookie text to a file at runtime
    with open('youtube_cookies.txt', 'w') as f:
        f.write(os.environ.get("YOUTUBE_COOKIES", ""))



    # yt-dlp options
    ydl_opts = {
    'outtmpl': download_path,
   'cookiefile': './www.youtube.com_cookies.txt',
   'cookiefile': './youtube_cookies.txt',

    'verbose': True
}

    # Download video using yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_filename = ydl.prepare_filename(info_dict)

    # Encode filename for URL
    safe_filename = quote(os.path.basename(video_filename))

    return f"""
    <h2>✅ Download Completed</h2>
    <a href="/get_video/{safe_filename}">➡ Click here to download your video</a><br><br>
    <small>File saved as: {video_filename}</small>
    """

# Serve Video File
@app.route('/get_video/<path:filename>')
def get_video(filename):
    try:
        return send_from_directory('downloads', filename, as_attachment=True)
    except FileNotFoundError:
        return "❌ File not found!", 404

# Run on Railway (or locally)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
