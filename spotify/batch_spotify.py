import tkinter as tk
from tkinter import scrolledtext
from url_artwork import process_spotify_link, get_spotify_access_token

def process_links():
    links = text_area.get("1.0", tk.END).strip().split('\n')
    for link in links:
        if link:
            process_spotify_link(link)

if __name__ == "__main__":
    # Initialize Spotify token once
    if not get_spotify_access_token():
        print("Failed to get Spotify access token. Please check your credentials in url_artwork.py")
    else:
        # Create the main window
        root = tk.Tk()
        root.title("Spotify Batch Processor")

        # Create a text area for input
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15)
        text_area.pack(padx=10, pady=10)

        # Create a button to process the links
        process_button = tk.Button(root, text="Process Links", command=process_links)
        process_button.pack(pady=5)

        # Start the GUI event loop
        root.mainloop()
