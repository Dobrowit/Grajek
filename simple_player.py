#!/usr/bin/python3

import requests
import schedule
import time
from datetime import datetime

API_BASE_URL = "http://IP_ADDR:8880/api/"
API_USERNAME = "LOGIN"
API_PASSWORD = "PASSWORD"
MAX_RETRIES = 1
RETRY_DELAY = 1


def log_request(url, status_code):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Request to {url} returned status code {status_code}")

def perform_request(url, method="POST", data=None):
    for attempt in range(MAX_RETRIES):
        try:
            if method == "POST":
                r = requests.post(url, auth=(API_USERNAME, API_PASSWORD), json=data)
            elif method == "GET":
                r = requests.get(url, auth=(API_USERNAME, API_PASSWORD))
            log_request(url, r.status_code)  
            if r.status_code in [200, 204]:
                return r.json() if r.text else {}
            elif r.status_code in [400, 404]:
                print(f"Error {r.status_code}: {r.json().get('error', {}).get('message', 'Unknown error')}")
                break
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Network Error: {e}")
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
    return perform_request(f"{API_BASE_URL}player", method="GET")

def get_playlist():
    return perform_request(f"{API_BASE_URL}playlist", method="GET")

def print_status():
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

def print_menu():
    print("\nMenu:\n1. Play Music\n2. Stop Music\n3. Set Volume\n4. Next Track\n5. Previous Track\n6. Choose Track\n7. Exit Menu\n8. Status")

def display_menu():
    print_status()
    print_menu()
    while True:
        choice = input("Choose an option: ")
        if choice == "1":
            play_music()
            break
        elif choice == "2":
            stop_music()
            break
        elif choice == "3":
            vol = input("Set volume (0-100): ")
            set_volume(int(vol))
        elif choice == "4":
            next_track()
        elif choice == "5":
            previous_track()
        elif choice == "6":
            playlist = get_playlist()
            tracks = playlist.get("items", [])
            for i, track in enumerate(tracks):
                print(f"{i + 1}. {track.get('title', 'Unknown')} ({track.get('duration', 'Unknown')}s)")
            track_no = int(input("Choose track number: ")) - 1
            if 0 <= track_no < len(tracks):
                perform_request(f"{API_BASE_URL}player/load_item", method="POST", data={"index": track_no})
            else:
                print("Invalid track number.")
        elif choice == "7":
            break
        elif choice == "8":
            print_status()
        else:
            print("Invalid option. Try again.")

schedule.every().day.at("09:00").do(play_music)
schedule.every().day.at("22:00").do(stop_music)

print_status()

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        display_menu()
