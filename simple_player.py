#!/usr/bin/python3

import requests
import schedule
import time

API_BASE_URL = "http://IP_ADDR:8880/api/"
API_USERNAME = "LOGIN"
API_PASSWORD = "PASSWORD"
MAX_RETRIES = 10
RETRY_DELAY = 30

def perform_request(url):
    for _ in range(MAX_RETRIES):
        try:
            r = requests.post(url, auth=(API_USERNAME, API_PASSWORD))
            if r.status_code in [200, 204]: return True
        except: pass
        time.sleep(RETRY_DELAY)
    return False

def play_music():
    perform_request(f"{API_BASE_URL}player/play")

def stop_music():
    perform_request(f"{API_BASE_URL}player/stop")

schedule.every().day.at("09:00").do(play_music)
schedule.every().day.at("22:00").do(stop_music)

while True:
    schedule.run_pending()
    time.sleep(1)
