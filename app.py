from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from downloader import extract_image_urls_from_website, download_image, ensure_directory, SAVE_DIR
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flashing messages

@app.route("/", methods=["GET", "POST"])
def index():
    images = []
    url = None

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            ensure_directory(SAVE_DIR)

            try:
                image_urls = extract_image_urls_from_website(url)
            except Exception as e:
                flash(f"Error fetching images: {e}", "danger")
                return redirect(url_for('index'))

            if not image_urls:
                flash("No images found on the page.", "warning")
            else:
                for i, img_url in enumerate(image_urls, start=1):
                    filename = download_image(img_url, i)
                    if filename:
                        images.append(filename)

                if not images:
                    flash("No valid images could be downloaded.", "warning")
                else:
                    flash(f"✅ Downloaded {len(images)} image(s).", "success")
        else:
            flash("Please enter a valid URL.", "warning")

    return render_template("index.html", images=images, url=url)

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == "__main__":
    os.makedirs(SAVE_DIR, exist_ok=True)
    app.run(debug=True)
