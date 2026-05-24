import requests as re
import json

import os
from dotenv import load_dotenv

load_dotenv("./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = os.getenv("CHANNEL_HANDLE")


def get_playlist():
    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

    try:

        response = re.get(url)

        response.raise_for_status()  # Check if the request was successful

        data = response.json()

        channel_items = data["items"][0]

        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]

        print(f"Channel Playlist ID: {channel_playlistId}")
        return channel_playlistId

    except re.exceptions.RequestException as e:
        raise e


def get_video_id(playlistId, max_results=10):

    video_ids = []
    page_token = None

    url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlistId}&key={API_KEY}"

    try:
        while True:
            params = {
                "part": "contentDetails",
                "maxResults": max_results,
                "playlistId": playlistId,
                "key": API_KEY,
            }
            if page_token:
                params["pageToken"] = page_token

            response = re.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            for item in items:
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        print(f"Video IDs: {video_ids}")
        return video_ids

    except re.exceptions.RequestException as e:
        raise e


if __name__ == "__main__":
    playlist_id = get_playlist()
    get_video_id(playlist_id)
