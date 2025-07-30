import pyperclip
import re
import os
import requests
import base64

# --- Spotify API Credentials ---
# IMPORTANT: Replace with your actual Client ID and Client Secret
# Get these from https://developer.spotify.com/dashboard/
CLIENT_ID = 'f01915fa55fb4e55bdefb16ed303fc89'
CLIENT_SECRET = '3d1f8ea1584240fd9556d2ff89f17a38'
# -------------------------------


def get_spotify_access_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {"grant_type": "client_credentials"}

    try:
        response = requests.post(token_url, headers=headers, data=body)
        response.raise_for_status()
        token_info = response.json()
        return token_info.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error getting Spotify access token: {e}")
        return None


def get_first_track_uri(item_type, item_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}

    if item_type == "playlist":
        api_url = f"https://api.spotify.com/v1/playlists/{item_id}/tracks?limit=1"
    elif item_type == "album":
        api_url = f"https://api.spotify.com/v1/albums/{item_id}/tracks?limit=1"
    else:
        return None

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if item_type == "playlist" and data.get("items") and data["items"][0].get("track"):
            return data["items"][0]["track"]["uri"]
        elif item_type == "album" and data.get("items") and data["items"][0].get("uri"):
            return data["items"][0]["uri"]
        else:
            print(f"Could not find first track for {item_type} ID: {item_id}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {item_type} tracks: {e}")
        return None


def get_item_details(item_type, item_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}

    if item_type == "playlist":
        api_url = f"https://api.spotify.com/v1/playlists/{item_id}"
    elif item_type == "album":
        api_url = f"https://api.spotify.com/v1/albums/{item_id}"
    else:
        return None, None, None

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        artwork_url = None
        images = data.get("images")
        if images and len(images) > 0:
            artwork_url = images[0]["url"]
        else:
            print(f"No artwork found for {item_type} ID: {item_id}")

        item_name = data.get("name")
        if not item_name:
            print(f"No name found for {item_type} ID: {item_id}")

        artist_name = None
        if item_type == "album":
            artists = data.get("artists")
            if artists and len(artists) > 0:
                artist_name = artists[0].get("name")
                if not artist_name:
                    print(f"No artist name found for album ID: {item_id}")
            else:
                print(f"No artists found for album ID: {item_id}")

        return artwork_url, item_name, artist_name
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {item_type} details: {e}")
        return None, None, None


def download_artwork(image_url, file_path):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)
        print(f"Artwork downloaded to: {file_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading artwork from {image_url}: {e}")
        return False


def process_spotify_link(url):
    spotify_url_pattern = re.compile(r"https://open\.spotify\.com/(playlist|album)/([a-zA-Z0-9]+)")
    match = spotify_url_pattern.search(url)

    if not match:
        print("Error: Clipboard content is not a valid Spotify playlist or album URL.")
        print(f"Found: {url}")
        return

    item_type = match.group(1)
    item_id = match.group(2)

    access_token = get_spotify_access_token()
    if not access_token:
        return

    first_track_uri = get_first_track_uri(item_type, item_id, access_token)
    context_uri = f"spotify:{item_type}:{item_id}"
    bat_play_command = f"start {first_track_uri}?context={context_uri}" if first_track_uri else f"start {context_uri}"

    artwork_url, item_name, artist_name = get_item_details(item_type, item_id, access_token)

    sanitized_item_name = re.sub(r'[\\/*?:"<>|]', "", item_name) if item_name else item_id

    directory = f"{item_type}s"
    if item_type == "album" and artist_name:
        sanitized_artist_name = re.sub(r'[\\/*?:"<>|]', "", artist_name)
        directory = os.path.join(directory, sanitized_artist_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    if artwork_url:
        artwork_file_name = f"{sanitized_item_name}.jpg"
        artwork_path = os.path.join(directory, artwork_file_name)
        download_artwork(artwork_url, artwork_path)

    bat_file_name = f"{sanitized_item_name}.bat"
    bat_path = os.path.join(directory, bat_file_name)
    bat_content = f"@echo off\n{bat_play_command}"

    try:
        with open(bat_path, "w") as f:
            f.write(bat_content)
        print(f"Successfully created '{bat_path}' with playback command.")
    except IOError as e:
        print(f"Error writing to '{bat_path}': {e}")


def create_spotify_bat_from_clipboard_and_play():
    try:
        clipboard_content = pyperclip.paste().strip()
        process_spotify_link(clipboard_content)
    except pyperclip.PyperclipException:
        print("Error: Could not access clipboard.")
        return


if __name__ == "__main__":
    if CLIENT_ID == 'YOUR_CLIENT_ID' or CLIENT_SECRET == 'YOUR_CLIENT_SECRET':
        print("WARNING: Please update CLIENT_ID and CLIENT_SECRET with your Spotify API credentials.")
    else:
        create_spotify_bat_from_clipboard_and_play()
