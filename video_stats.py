from os import name

import requests as re
import json

API_KEY = "AIzaSyDSF5aHIihvxdDuDZLVmQjMCgnvqkcbjuM"
CHANNEL_HANDLE = "MrBeast"


def get_playlist():
    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

    try:

        response = re.get(url)

        response.raise_for_status()  # Check if the request was successful

        data = response.json()

        # print(json.dumps(data, indent=4))

        channel_items = data["items"][0]

        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        
        print(f"Channel Playlist ID: {channel_playlistId}")
        return channel_playlistId

    except re.RequestException as e:
        raise e


if __name__ == "__main__":
    get_playlist()
    