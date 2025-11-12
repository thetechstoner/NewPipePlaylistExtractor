#!/usr/bin/env python3

# playlists-convert-grayjay.py
#
# Extracts all files from the input Grayjay ZIP to memory
# Reads playlists CSV with names and lists of URLs/playlist URLs
# For YouTube remote playlists, uses yt-dlp to expand to individual video URLs
# Converts all playlists to the Grayjay local playlist format (name + uuid + video URLs)
# Updates the cache_videos with video info stubs parsed from URLs
# Updates stores/Playlists with the local playlists
# Writes everything into a new Grayjay export ZIP preserving other files untouched
#
# Usage Example:
# python3 playlists-convert-grayjay.py Grayjay-Zip-Template.zip playlists.csv grayjay-export.zip
#
# - The first argument is the input Grayjay Template zip file.
# - The second argument is the input playlists csv file.
# - the third argument is the output grayjay export zip file.

import sys
import os
import zipfile
import json
import csv
import io
import tempfile
from yt_dlp import YoutubeDL

def load_grayjay_template(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        file_contents = {name: z.read(name) for name in z.namelist()}
    return file_contents

def save_grayjay_export(file_contents, output_path):
    with zipfile.ZipFile(output_path, 'w') as z:
        for name, data in file_contents.items():
            z.writestr(name, data)

def parse_playlists_csv(csv_path):
    playlists = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            playlist_name = row[0]
            # row[1] might be a string representation of list of urls or a playlist url
            urls_str = row[1]
            # Attempt to eval urls list if it's a list string, else treat as single URL
            urls = []
            try:
                urls = eval(urls_str)
                if not isinstance(urls, list):
                    urls = [urls_str]
            except:
                urls = [urls_str]
            playlists.append((playlist_name, urls))
    return playlists

def expand_youtube_playlist(playlist_url):
    # Use yt-dlp to get video URLs from remote playlist
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'forceurl': True,
        'forcejson': True,
        'ignoreerrors': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(playlist_url, download=False)
            entries = info.get('entries', [])
            video_urls = []
            for entry in entries:
                if entry and 'url' in entry:
                    video_urls.append(f"https://www.youtube.com/watch?v={entry['url']}")
            return video_urls
        except Exception as e:
            print(f"Failed to expand playlist {playlist_url}: {e}")
            return []

def convert_playlists_to_local(playlists):
    # playlists is list of (name, [urls])
    local_playlists = []
    for name, urls in playlists:
        all_video_urls = []
        for url in urls:
            # Heuristic: if url has "playlist" param, expand it, else treat as single video or local url
            if "list=" in url and ("youtube.com" in url or "youtu.be" in url):
                expanded = expand_youtube_playlist(url)
                all_video_urls.extend(expanded)
            else:
                # treat as local video url in grayjay format
                all_video_urls.append(url)
        # Compose local playlist string for Grayjay (name:::uuid and list of URLs)
        # For simplicity, generate a dummy UUID based on name
        import uuid
        playlist_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
        # Compose as one string: name:::uuid newline separated URLs
        playlist_str = name + ":::" + playlist_id + "\n" + "\n".join(all_video_urls)
        local_playlists.append(playlist_str)
    return local_playlists

def update_grayjay_cache_videos(file_contents, all_video_urls):
    # Compose cache_videos as JSON list of video dicts
    # For simplicity, each video dict has id.value = video ID from URL, platform= "YouTube", pluginId is YouTube plugin id from example
    # Extract video IDs from URLs, form minimal dicts
    plugin_id_youtube = "35ae969a-a7db-11ed-afa1-0242ac120002"
    cache_videos = []
    for url in all_video_urls:
        # parse video id from "https://www.youtube.com/watch?v=VIDEOID" or "youtu.be/VIDEOID"
        from urllib.parse import urlparse, parse_qs
        vid_id = None
        try:
            parsed = urlparse(url)
            if "youtube.com" in parsed.netloc:
                qs = parse_qs(parsed.query)
                vid_id = qs.get('v',[None])[0]
            elif "youtu.be" in parsed.netloc:
                vid_id = parsed.path.lstrip('/')
            if vid_id:
                video_entry = {
                    "id": {"platform": "YouTube", "value": vid_id, "pluginId": plugin_id_youtube},
                    "name": "",  # no name info here - can be empty or later enhanced
                    "thumbnails": {"sources": []},
                    "author": {"id": {}, "name": "", "url": "", "thumbnail": "", "subscribers": 0},
                    "datetime": 0,
                    "url": url,
                    "shareUrl": url,
                    "duration": 0,
                    "viewCount": 0
                }
                cache_videos.append(video_entry)
        except Exception as e:
            print(f"Skipping invalid url {url}: {e}")
    file_contents['cache_videos'] = json.dumps(cache_videos, ensure_ascii=False).encode('utf-8')

def update_grayjay_playlists(file_contents, local_playlists):
    # Update stores/Playlists file in JSON (list of local playlist strings)
    file_contents['stores/Playlists'] = json.dumps(local_playlists, ensure_ascii=False).encode('utf-8')

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 playlists-convert-grayjay.py Grayjay-Zip-Template.zip playlists.csv grayjay-export.zip")
        sys.exit(1)
    template_zip = sys.argv[1]
    csv_file = sys.argv[2]
    output_zip = sys.argv[3]

    # Load Grayjay template zip contents
    file_contents = load_grayjay_template(template_zip)

    # Parse playlists CSV
    playlists = parse_playlists_csv(csv_file)

    # Convert remote playlists to local playlists (expands YouTube playlists)
    local_playlists = convert_playlists_to_local(playlists)

    # Flatten all video URLs to update cache_videos
    all_video_urls = []
    for pl_str in local_playlists:
        lines = pl_str.split('\n')
        all_video_urls.extend(lines[1:])  # skip name line

    # Update cache_videos and stores/Playlists in file_contents
    update_grayjay_cache_videos(file_contents, all_video_urls)
    update_grayjay_playlists(file_contents, local_playlists)

    # Save updated contents to new export zip
    save_grayjay_export(file_contents, output_zip)

    print(f"Grayjay export ZIP created: {output_zip}")

if __name__ == "__main__":
    main()
