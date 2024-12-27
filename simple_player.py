#!/usr/bin/python3

import requests
import schedule
import time
import keyboard

API_BASE_URL = "http://IP_ADDR:8880/api/"
API_USERNAME = "LOGIN"
API_PASSWORD = "PASSWORD"
MAX_RETRIES = 10
RETRY_DELAY = 30

def perform_request(url, method="POST", data=None):
    for _ in range(MAX_RETRIES):
        try:
            if method == "POST":
                #r = requests.post(url, auth=(API_USERNAME, API_PASSWORD), json=data)
                r = 200
            elif method == "GET":
                #r = requests.get(url, auth=(API_USERNAME, API_PASSWORD))
                r = 200
            if r.status_code in [200, 204]:
                return r.json() if r.text else {}
        except: pass
        time.sleep(RETRY_DELAY)
    return {}

def play_music():
    perform_request(f"{API_BASE_URL}player/play")

def stop_music():
    perform_request(f"{API_BASE_URL}player/stop")

def set_volume(volume):
    perform_request(f"{API_BASE_URL}player/set_volume", method="POST", data={"volume": volume})

def next_track():
    perform_request(f"{API_BASE_URL}player/next")

def previous_track():
    perform_request(f"{API_BASE_URL}player/prev")

def get_status():
    return perform_request(f"{API_BASE_URL}player/status", method="GET")

def get_playlist():
    return perform_request(f"{API_BASE_URL}playlist", method="GET")

schedule.every().day.at("09:00").do(play_music)
schedule.every().day.at("22:00").do(stop_music)

while True:
    schedule.run_pending()
    if keyboard.is_pressed("ctrl+m"):
        status = get_status()
        playlist = get_playlist()
        volume = status.get("state", {}).get("volume", "Unknown")
        current_track = status.get("state", {}).get("active_item", {})
        current_title = current_track.get("title", "Unknown")
        current_length = current_track.get("duration", "Unknown")
        state = status.get("state", {}).get("is_playing", False)
        tracks = playlist.get("items", [])
        total_tracks = len(tracks)
        total_time = sum(item.get("duration", 0) for item in tracks)

        print(f"\nStatus:\nVolume: {volume}\nCurrent Track: {current_title} ({current_length}s)\nState: {'Playing' if state else 'Stopped'}")
        print(f"Total Tracks: {total_tracks}\nTotal Time: {total_time}s")
        print("\nMenu:\n1. Play Music\n2. Stop Music\n3. Set Volume\n4. Next Track\n5. Previous Track\n6. Choose Track\n7. Exit Menu")

        while True:
            choice = input("Choose an option: ")
            if choice == "1":
                play_music()
                print("Music started.")
                break
            elif choice == "2":
                stop_music()
                print("Music stopped.")
                break
            elif choice == "3":
                vol = input("Set volume (0-100): ")
                set_volume(int(vol))
                print(f"Volume set to {vol}.")
            elif choice == "4":
                next_track()
                print("Skipped to next track.")
            elif choice == "5":
                previous_track()
                print("Reverted to previous track.")
            elif choice == "6":
                for i, track in enumerate(tracks):
                    print(f"{i + 1}. {track.get('title', 'Unknown')} ({track.get('duration', 'Unknown')}s)")
                track_no = int(input("Choose track number: ")) - 1
                if 0 <= track_no < total_tracks:
                    perform_request(f"{API_BASE_URL}player/load_item", method="POST", data={"index": track_no})
                    print("Track selected.")
                else:
                    print("Invalid track number.")
            elif choice == "7":
                print("Exiting menu.")
                break
            else:
                print("Invalid option. Try again.")
    time.sleep(1)
