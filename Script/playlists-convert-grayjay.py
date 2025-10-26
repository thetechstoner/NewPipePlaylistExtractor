#!/usr/bin/env python3

import csv
import json
import uuid
import os
import ast
import zipfile

def generate_uuid():
    return str(uuid.uuid4())

def main():
    # Output directory structure
    export_dir = "grayjay-export"
    os.makedirs(export_dir, exist_ok=True)
    os.makedirs(os.path.join(export_dir, "stores"), exist_ok=True)

    # --- exportInfo ---
    export_info = {"version": "1"}
    with open(os.path.join(export_dir, "exportInfo"), "w", encoding="utf-8") as f:
        json.dump(export_info, f, separators=(',', ':'))

    # --- plugin_settings ---
    plugin_settings = {
        "4a78c2ff-c20f-43ac-8f75-34515df1d320": {},
        "8d029a7f-5507-4e36-8bd8-c19a3b77d383": {},
        "4e365633-6d3f-4267-8941-fdc36631d813": {},
        "35ae969a-a7db-11ed-afa1-0242ac120002": {
            "youtubeDislikerHeader": None,
            "sponsorBlockCat_Filler": "0",
            "allow_ump_backoff": "false",
            "fallback_home_trending": "true",
            "allowLoginFallback": "true",
            "advanced": None,
            "sponsorBlockCat_Intro": "0",
            "useAggressiveUMPRecovery": "true",
            "notify_ump_recovery": "false",
            "channelRssOnly": "false",
            "sponsorBlockNoVotes": "false",
            "isInlinePlaybackNoAd_login": "false",
            "allowMemberContent": "true",
            "verifyIOSPlayback": "true",
            "sponsorBlockCat_Sponsor": "1",
            "allow_av1": "false",
            "allowControversialRestricted": "true",
            "isInlinePlaybackNoAd": "false",
            "youtubeActivity": "false",
            "allowAgeRestricted": "true",
            "sponsorBlockCat_Outro": "0",
            "sponsorBlock": "true",
            "notify_cipher": "false",
            "notify_bg": "false",
            "sponsorBlockCat_Self": "0",
            "allow_ump_backoff_async": "true",
            "sponsorBlockCat_Offtopic": "0",
            "authChannels": "false",
            "youtubeDislikes": "false",
            "showVerboseToasts": "false",
            "sponsorBlockHeader": None,
            "sponsorBlockCat_Preview": "0",
            "allow_ump_plugin_reloads": "true",
            "useUMP": "false",
            "authDetails": "false"
        },
        "2ce7b35e-d2b2-4adb-a728-a34a30d30359": {},
        "9d703ff5-c556-4962-a990-4f000829cb87": {},
        "84331338-b045-419c-88e4-c86036f4cbf5": {},
        "cf8ea74d-ad9b-489e-a083-539b6aa8648c": {},
        "5fb74e28-2fba-406a-9418-38af04f63c08": {},
        "c0f315f9-0992-4508-a061-f2738724c331": {},
        "9bb33039-8580-48d4-9849-21319ae845a4": {},
        "e8b1ad5f-0c6d-497d-a5fa-0a785a16d902": {},
        "9c87e8db-e75d-48f4-afe5-2d203d4b95c5": {},
        "aac9e9f0-24b5-11ee-be56-0242ac120002": {},
        "1c291164-294c-4c2d-800d-7bc6d31d0019": {},
        "273b6523-5438-44e2-9f5d-78e0325a8fd9": {},
        "1c05bfc3-08b9-42d0-93d3-6d52e0fd34d8": {},
        "89ae4889-0420-4d16-ad6c-19c776b28f99": {}
    }
    with open(os.path.join(export_dir, "plugin_settings"), "w", encoding="utf-8") as f:
        json.dump(plugin_settings, f, separators=(',', ':'))

    # --- plugins ---
    plugins = {
        "4a78c2ff-c20f-43ac-8f75-34515df1d320": "https://plugins.grayjay.app/Kick/KickConfig.json",
        "8d029a7f-5507-4e36-8bd8-c19a3b77d383": "https://plugins.grayjay.app/TedTalks/TedTalksConfig.json",
        "4e365633-6d3f-4267-8941-fdc36631d813": "https://plugins.grayjay.app/Spotify/SpotifyConfig.json",
        "35ae969a-a7db-11ed-afa1-0242ac120002": "https://plugins.grayjay.app/Youtube/YoutubeConfig.json",
        "2ce7b35e-d2b2-4adb-a728-a34a30d30359": "https://plugins.grayjay.app/Rumble/RumbleConfig.json",
        "9d703ff5-c556-4962-a990-4f000829cb87": "https://plugins.grayjay.app/Nebula/NebulaConfig.json",
        "84331338-b045-419c-88e4-c86036f4cbf5": "https://plugins.grayjay.app/Mixcloud/MixcloudConfig.json",
        "cf8ea74d-ad9b-489e-a083-539b6aa8648c": "https://plugins.grayjay.app/Bilibili/BiliBiliConfig.json",
        "5fb74e28-2fba-406a-9418-38af04f63c08": "https://plugins.grayjay.app/Soundcloud/SoundcloudConfig.json",
        "c0f315f9-0992-4508-a061-f2738724c331": "https://plugins.grayjay.app/Twitch/TwitchConfig.json",
        "9bb33039-8580-48d4-9849-21319ae845a4": "https://plugins.grayjay.app/Crunchyroll/CrunchyrollConfig.json",
        "e8b1ad5f-0c6d-497d-a5fa-0a785a16d902": "https://plugins.grayjay.app/Bitchute/BitchuteConfig.json",
        "9c87e8db-e75d-48f4-afe5-2d203d4b95c5": "https://plugins.grayjay.app/Dailymotion/DailymotionConfig.json",
        "aac9e9f0-24b5-11ee-be56-0242ac120002": "https://plugins.grayjay.app/Patreon/PatreonConfig.json",
        "1c291164-294c-4c2d-800d-7bc6d31d0019": "https://plugins.grayjay.app/PeerTube/PeerTubeConfig.json",
        "273b6523-5438-44e2-9f5d-78e0325a8fd9": "https://plugins.grayjay.app/CuriosityStream/CuriosityStreamConfig.json",
        "1c05bfc3-08b9-42d0-93d3-6d52e0fd34d8": "https://plugins.grayjay.app/Odysee/OdyseeConfig.json",
        "89ae4889-0420-4d16-ad6c-19c776b28f99": "https://plugins.grayjay.app/ApplePodcasts/ApplePodcastsConfig.json"
    }
    with open(os.path.join(export_dir, "plugins"), "w", encoding="utf-8") as f:
        json.dump(plugins, f, separators=(',', ':'))

    # --- stores/Playlists ---
    playlists_path = os.path.join(export_dir, "stores", "Playlists")
    playlists = []

    with open("playlists.csv", newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or not row[0].strip():
                continue
            name = row[0].strip()
            if len(row) > 1:
                try:
                    urls = ast.literal_eval(row[1].strip())
                except Exception:
                    urls = []
            else:
                urls = []

            for url in urls:
                entry = f"{name}:::{generate_uuid()}\n{url}"
                playlists.append(entry)

    with open(playlists_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(playlists, ensure_ascii=False))

    # --- Pack zip ---
    with zipfile.ZipFile("grayjay-export.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(export_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                arc_name = os.path.relpath(abs_path, export_dir)
                zipf.write(abs_path, arc_name)

    print("grayjay-export.zip created successfully.")

if __name__ == "__main__":
    main()
