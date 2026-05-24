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

        #print(f"Channel Playlist ID: {channel_playlistId}")
        return channel_playlistId

    except re.exceptions.RequestException as e:
        raise e


def get_video_id(playlistId, max_results=50):

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

        #print(f"Video IDs: {video_ids}")
        return video_ids

    except re.exceptions.RequestException as e:
        raise e


def batch_video_ids(video_ids, batch_size=50):
    for i in range(0, len(video_ids), batch_size):
        yield video_ids[i : i + batch_size]


def get_video_data(video_ids):
    url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id=vBEGODNmdas&key={API_KEY}"

    video_data = []

    try:
        for batch in batch_video_ids(video_ids):
            params = {
                "part": "statistics",
                "id": ",".join(batch),
                "key": API_KEY,
            }

            response = re.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            for item in items:
                video_id = item["id"]
                snippet = item["snippet"]
                content_details = item["contentDetails"]
                stats = item["statistics"]
                video_data.append({"video_id": video_id, "title": snippet["title"], "publishedAt": snippet["publishedAt"], "duration": content_details["duration"], "views": stats.get("viewCount", None), "likesCount": stats.get("likeCount", None), "commentsCount": stats.get("commentCount", None)})

        print(f"Video Data: {video_data}")
        return video_data

    except re.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlist_id = get_playlist()
    video_ids = get_video_id(playlist_id)
    get_video_data(video_ids)
