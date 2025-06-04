import os
import json
import flickrapi
import requests
from PIL import Image, ImageDraw

# Replace these with your own Flickr API credentials
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

# Set up the Flickr API client
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format="parsed-json")

# Load the downloaded images list
downloaded_images_file = "downloaded_images.json"
if os.path.exists(downloaded_images_file):
    with open(downloaded_images_file, "r") as f:
        downloaded_images = json.load(f)
else:
    downloaded_images = []

def search_images(search_term):
    results = flickr.photos.search(
        text=search_term,
        per_page=10,
        media="photos",
        sort="relevance",
        safe_search=1,
        extras="url_q,license",
        content_type=7
    )
    return results["photos"]["photo"]

def download_image(url, file_path):
    response = requests.get(url)
    with open(file_path, "wb") as f:
        f.write(response.content)
    downloaded_images.append(file_path)
    with open(downloaded_images_file, "w") as f:
        json.dump(downloaded_images, f)

def display_image(image_path, is_downloaded=False):
    im = Image.open(image_path)
    if is_downloaded:
        draw = ImageDraw.Draw(im)
        draw.rectangle([(0, 0), (im.width - 1, im.height - 1)], outline="red", width=5)
    im.show()

def main():
    search_term = input("Enter a search term: ")
    images = search_images(search_term)

    while True:
        for idx, img in enumerate(images, start=1):
            print(f"{idx}. {img['title']}")

        selected = input("Enter image number(s) to download (comma-separated) or 'q' to quit: ")

        if selected.lower() == "q":
            break

        selected_indices = [int(x) - 1 for x in selected.split(",")]

        for idx in selected_indices:
            img = images[idx]
            url = img["url_q"]
            file_path = f"{img['id']}_{search_term}.jpg"

            if file_path in downloaded_images:
                print(f"{img['title']} has already been downloaded.")
            else:
                download_image(url, file_path)
                print(f"{img['title']} has been downloaded.")

            display_image(file_path, is_downloaded=True)

if __name__ == "__main__":
    main()
