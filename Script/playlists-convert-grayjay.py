#!/usr/bin/env python3

# playlists-convert-grayjay.py
#
# Reads your CSV playlists file (local and remote).
# Expands remote playlists fully into video lists.
# Produces GrayJay-compatible export in a zip file.
#
# Usage Example:
# python3 playlists-convert-grayjay.py playlists.csv grayjay-export.zip
#
# - The first argument is the input playlists CSV file.
# - The second argument is the output grayjay-export ZIP archive

import csv
import json
import uuid
import os
import ast
import re
import sys
import zipfile
from yt_dlp import YoutubeDL

def generate_uuid():
    return str(uuid.uuid4())

def is_remote_playlist(url):
    patterns = [
        r'(?:youtube\.com|youtu\.be).*(list=|/playlist\?id=)',
        r'(?:odysee\.com|odysee\.tv).*/playlist/',
        r'(?:peertube\.)'
    ]
    pattern = re.compile('|'.join(patterns), re.IGNORECASE)
    return bool(pattern.search(url))

def expand_remote_playlist(url):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,
    }
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [])
            video_urls = []
            for entry in entries:
                video_url = entry.get('url') or entry.get('webpage_url')
                if video_url:
                    video_urls.append(video_url)
            return video_urls
        except Exception as e:
            print(f"Failed to expand remote playlist {url}: {e}")
            return []

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 playlists-convert-grayjay.py playlists.csv grayjay-export.zip")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_zip = sys.argv[2]

    export_dir = "grayjay-export"
    os.makedirs(export_dir, exist_ok=True)
    os.makedirs(os.path.join(export_dir, "stores"), exist_ok=True)

    playlists_path = os.path.join(export_dir, "stores", "Playlists")

    playlist_entries = []

    with open(input_csv, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or not row[0].strip():
                continue

            playlist_name = row[0].strip()
            urls = []
            if len(row) > 1:
                try:
                    urls = ast.literal_eval(row[1].strip())
                except Exception:
                    urls = []

            # Expand remote playlist if single URL and is remote playlist URL
            if len(urls) == 1 and is_remote_playlist(urls[0]):
                expanded_urls = expand_remote_playlist(urls[0])
                if expanded_urls:
                    urls = expanded_urls

            # Compose single entry string: playlistname:::uuid \n url1 \n url2 ...
            videos_str = "\n".join(urls)
            entry = f"{playlist_name}:::{generate_uuid()}\n{videos_str}"
            playlist_entries.append(entry)

    with open(playlists_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(playlist_entries, ensure_ascii=False))

    # Zip the export directory to output zip file
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(export_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                arc_name = os.path.relpath(abs_path, export_dir)
                zipf.write(abs_path, arc_name)

    print(f"{output_zip} created successfully.")

if __name__ == "__main__":
    main()
