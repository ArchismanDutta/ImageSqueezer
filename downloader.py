import requests
import os
import mimetypes
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuration
SAVE_DIR = "images"
VALID_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/bmp']

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://craftedmemories.us"
}

# Ensure target directory exists
def ensure_directory(path):
    os.makedirs(path, exist_ok=True)

# Normalize extension if needed (e.g. .jpe -> .jpg)
def normalize_extension(ext):
    if ext == ".jpe":
        return ".jpg"
    return ext

# Guess file extension based on content-type
def get_file_extension(content_type):
    extension = mimetypes.guess_extension(content_type)
    return normalize_extension(extension) if extension else ".webp"

# Validate the image type
def is_valid_image_type(content_type):
    return content_type.split(";")[0] in VALID_IMAGE_TYPES

# Avoid overwriting existing files
def get_unique_filename(base_path, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(base_path, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    return new_filename

# Download a single image
def download_image(url, count):
    ensure_directory(SAVE_DIR)

    try:
        response = requests.get(url, stream=True, headers=HEADERS, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        print(f"🔍 URL {count}: {url}")
        print(f"    ↳ Content-Type: {content_type if content_type else '[empty]'}")

        if not content_type:
            ext = ".webp"
            print("⚠️  No Content-Type. Assuming .webp")
        elif not is_valid_image_type(content_type):
            print(f"⚠️  Skipping: Not a recognized image (Content-Type: {content_type})")
            return None
        else:
            ext = get_file_extension(content_type)

        filename = get_unique_filename(SAVE_DIR, f"image_{count}{ext}")
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"✅ Saved: {filepath}")
        return filename

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {url}:\n   {e}")
        return None

# Extract all image URLs from a given webpage
def extract_image_urls_from_website(website_url):
    try:
        response = requests.get(website_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch website:\n   {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")

    image_urls = set()
    for img in img_tags:
        src = img.get("src")
        if not src:
            continue
        full_url = urljoin(website_url, src)
        image_urls.add(full_url)

    return list(image_urls)

# Main execution
def main():
    ensure_directory(SAVE_DIR)

    website_url = input("🌐 Enter website URL to scan for images: ").strip()
    if not website_url:
        print("❌ No URL provided.")
        return

    image_urls = extract_image_urls_from_website(website_url)

    if not image_urls:
        print("⚠️ No images found on the page.")
        return

    print(f"\n📸 Found {len(image_urls)} image(s):\n")
    for i, url in enumerate(image_urls, start=1):
        print(f"  {i}. {url}")

    print("\n⬇️ Starting download...\n")
    for count, url in enumerate(image_urls, start=1):
        download_image(url, count)

# Run the script
if __name__ == "__main__":
    main()
