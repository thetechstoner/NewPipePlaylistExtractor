#!/usr/bin/env python3

import json
import uuid
import time
import zipfile
from yt_dlp import YoutubeDL

def generate_random_uuid():
    return str(uuid.uuid4())

def get_current_timestamp_ms():
    return int(time.time() * 1000)

def process_video(url):
    opts = {
        'quiet': True,
        'no_warnings': True,
    }

    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Failed to extract info for {url}: {e}")
            return None

    return {
        "videoId": info.get("id"),
        "title": info.get("title"),
        "author": info.get("uploader"),
        "authorId": info.get("channel_id"),
        "lengthSeconds": info.get("duration"),
        "published": int(info.get("timestamp", 0)) * 1000 if info.get("timestamp") else None,
        "timeAdded": get_current_timestamp_ms(),
        "playlistItemId": generate_random_uuid(),
        "type": "video"
    }

def process_playlist(playlist_name, urls):
    current_ts = get_current_timestamp_ms()
    _id = "ft-playlist--" + generate_random_uuid()
    videos = []

    for url in urls:
        url = url.strip()
        if not url:
            continue
        video = process_video(url)
        if video:
            videos.append(video)

    last_updated = max((v["timeAdded"] for v in videos), default=current_ts)
    return {
        "playlistName": playlist_name,
        "protected": False,
        "description": "",
        "videos": videos,
        "_id": _id,
        "createdAt": current_ts,
        "lastUpdatedAt": last_updated
    }

def extract_grayjay_playlists(zip_path):
    playlists = []
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open("stores/Playlists") as f:
            data = json.load(f)

    # Each entry is formatted like: "tech2:::03d42e49...\nhttps://youtube.com/..."
    for entry in data:
        try:
            name_part, url_part = entry.split("\n")
            playlist_name = name_part.split(":::")[0]
            url = url_part.strip()
            playlists.append((playlist_name, url))
        except Exception as e:
            print(f"Skipping malformed entry: {entry} ({e})")
            continue

    grouped = {}
    for name, url in playlists:
        grouped.setdefault(name, []).append(url)

    return grouped

def main():
    zip_path = "grayjay-export.zip"
    output_file = "freetube-playlists.db"

    grayjay_playlists = extract_grayjay_playlists(zip_path)

    with open(output_file, "w", encoding="utf-8") as db:
        # FreeTube requires a Favorites playlist
        ts = get_current_timestamp_ms()
        favorites = {
            "playlistName": "Favorites",
            "protected": False,
            "description": "Your favorite videos",
            "videos": [],
            "_id": "favorites",
            "createdAt": ts,
            "lastUpdatedAt": ts
        }
        db.write(json.dumps(favorites, separators=(',', ':')) + "\n")

        # Convert each Grayjay playlist
        for playlist_name, urls in grayjay_playlists.items():
            print(f"Converting: {playlist_name} ({len(urls)} videos)")
            ft_playlist = process_playlist(playlist_name, urls)
            db.write(json.dumps(ft_playlist, separators=(',', ':')) + "\n")

    print(f"{output_file} created successfully.")

if __name__ == "__main__":
    main()
