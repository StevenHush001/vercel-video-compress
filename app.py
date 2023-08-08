import os
import subprocess
from flask import Flask, request, render_template, send_file
import requests

app = Flask(__name__)

researchData = []

def get_video_size(url):
    if "http" in url:
        response = requests.head(url, allow_redirects=True)
        return int(response.headers.get("Content-Length", 0))
    else:
        return os.path.getsize(url)
    
def reduce_video_file_size_with_sharpen(output_file, input_file, crf, yadif):
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_file,
                "-vf",
                (
                    "unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=1.5,"
                    "hqdn3d=luma_spatial=2:chroma_spatial=1:luma_tmp=3:chroma_tmp=2,"
                    "eq=brightness=-0.1:contrast=1.2:saturation=1.2:gamma=1.2,"
                    f"yadif={yadif}"
                ),
                "-crf",
                f"{crf}",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                output_file,
            ]
        )
        
        original_size_mb = get_video_size(input_file) / (1024 * 1024)
        video_size_mb = get_video_size(output_file) / (1024 * 1024)

        return {
            "input_size_mb": original_size_mb,
            "output_size_mb": video_size_mb,
            "success": True
        }

    except Exception as e:
        return {
            "error": f"Error reducing video file size with sharpening: {e}",
            "success": False
        }


# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         input_file_url = request.form["input_file_url"]
#         name = request.form["name"]

#         # Process the video
#         reduce_video_file_size_with_sharpen(
#             f"output/{name}.mp4", input_file_url, 32.5, 2
#         )

#         # Provide the processed video for download
#         processed_video = f"output/{name}.mp4"
#         return send_file(processed_video, as_attachment=True)

#     return render_template("index.html")

@app.route('/', methods=['GET', 'POST'])
def index():
    input_size_mb = None
    output_size_mb = None

    if request.method == 'POST':
        input_file_url = request.form['input_file_url']
        name = request.form['name']

        result = reduce_video_file_size_with_sharpen(
            f"output/{name}.mp4", input_file_url, 32.5, 2
        )

        if result.get("success"):
            input_size_mb = result["input_size_mb"]
            output_size_mb = result["output_size_mb"]

            processed_video = f"output/{name}.mp4"
            return send_file(processed_video, as_attachment=True)

    return render_template('index.html', input_size_mb=input_size_mb, output_size_mb=output_size_mb)


if __name__ == "__main__":
     app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT', 5000))
