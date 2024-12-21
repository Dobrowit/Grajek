#!/usr/bin/python3

import requests
import schedule
import time
from datetime import datetime

# Configuration of the base API URL and authentication data
API_BASE_URL = "http://IP_ADDR:8880/api/"
API_USERNAME = "LOGIN"  # Enter your username
API_PASSWORD = "PASSWORD"  # Enter your password

# Configuration of the number of retries and delay between them
MAX_RETRIES = 10  # Maximum number of connection retry attempts
RETRY_DELAY = 30  # Delay between retries in seconds

def log_event(message):
    """Logs an event with date and time.

    Args:
        message (str): Content of the logged event.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def perform_request(url):
    """Executes a POST request with multiple retry attempts.

    Args:
        url (str): URL to which the POST request is sent.

    Returns:
        bool: True if the request was successful, False otherwise.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Perform a POST request with HTTP Basic Auth
            response = requests.post(url, auth=(API_USERNAME, API_PASSWORD))
            if response.status_code in [200, 204]:  # 200: OK, 204: No Content
                return True
            else:
                log_event(f"Request error: {response.status_code}")
                return False
        except requests.RequestException as e:
            # Handle connection errors to the server
            log_event(f"Connection error (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)  # Wait before the next attempt
            else:
                log_event("Connection retry limit exceeded.")
                return False

def play_music():
    """Starts music playback."""
    if perform_request(f"{API_BASE_URL}player/play"):
        log_event("Music playback started.")

def stop_music():
    """Stops music playback."""
    if perform_request(f"{API_BASE_URL}player/stop"):
        log_event("Music playback stopped.")

# Logging configuration
log_event("API URL base: " + API_BASE_URL)

# Task scheduling - daily activation at specified times
schedule.every().day.at("09:00").do(play_music)  # Start music at 9:00 AM
schedule.every().day.at("22:00").do(stop_music)  # Stop music at 10:00 PM

# Information about starting the scheduler
log_event("Scheduler started. The script is running in the background.")

# Main application loop - executing tasks according to the schedule
while True:
    schedule.run_pending()  # Execute scheduled tasks
    time.sleep(1)  # Short pause to avoid excessive CPU usage
