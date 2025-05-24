#!/usr/bin/env python3

import json

def freetube_video_to_url(video):
    """
    Construct a YouTube video URL from FreeTube video object.
    """
    video_id = video.get("videoId")
    if not video_id:
        return None
    return f"https://youtube.com/watch?v={video_id}"

def convert_freetube_db_to_piped_json():
    playlists = []

    with open('freetube-playlists.db', 'r', encoding='utf-8') as db_file:
        for line in db_file:
            try:
                playlist = json.loads(line)
            except Exception:
                continue

            # Skip FreeTube's default "Favorites" playlist
            if playlist.get("playlistName", "").lower() == "favorites":
                continue

            name = playlist.get("playlistName", "Unnamed Playlist")
            videos = playlist.get("videos", [])
            urls = []
            for video in videos:
                url = freetube_video_to_url(video)
                if url:
                    urls.append(url)

            playlist_obj = {
                "name": name,
                "type": "playlist",
                "visibility": "private",
                "videos": urls
            }
            playlists.append(playlist_obj)

    output = {
        "format": "Piped",
        "version": 1,
        "playlists": playlists
    }

    with open('playlists-piped.json', 'w', encoding='utf-8') as out_file:
        json.dump(output, out_file, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    convert_freetube_db_to_piped_json()
