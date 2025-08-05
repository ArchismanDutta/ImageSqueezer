# app.py

from flask import Flask, render_template, request, send_from_directory
from downloader import extract_image_urls_from_website, download_image, ensure_directory, SAVE_DIR
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    url = None

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            ensure_directory(SAVE_DIR)
            image_urls = extract_image_urls_from_website(url)
            for i, img_url in enumerate(image_urls, start=1):
                if download_image(img_url, i):
                    images.append(f"image_{i}.webp")  # assumes .webp fallback or update logic to detect correct ext

    return render_template("index.html", images=images, url=url)
    print("📩 Request method:", request.method)


@app.route("/images/<filename>")
def serve_image(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == "__main__":
    os.makedirs(SAVE_DIR, exist_ok=True)
    app.run(debug=True)
