#!/usr/bin/python3

import requests
import schedule
import time
from datetime import datetime

# Konfiguracja bazowego URL API i danych uwierzytelniających
API_BASE_URL = "http://IP_ADDR:8880/api/"
API_USERNAME = "login"  # Wprowadź swój login
API_PASSWORD = "password"  # Wprowadź swoje hasło

# Konfiguracja liczby prób i opóźnienia pomiędzy nimi
MAX_RETRIES = 10  # Maksymalna liczba prób ponowienia połączenia
RETRY_DELAY = 30  # Opóźnienie między próbami w sekundach

def log_event(message):
    """Loguje zdarzenie z datą i godziną.

    Args:
        message (str): Treść logowanego zdarzenia.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def perform_request(url):
    """Wykonuje żądanie POST z wielokrotnymi próbami.

    Args:
        url (str): URL do którego wysyłane jest żądanie POST.

    Returns:
        bool: True jeśli żądanie zakończyło się sukcesem, False w przeciwnym razie.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Wykonanie żądania POST z uwierzytelnieniem HTTP Basic Auth
            response = requests.post(url, auth=(API_USERNAME, API_PASSWORD))
            if response.status_code in [200, 204]:  # 200: OK, 204: No Content
                return True
            else:
                log_event(f"Błąd żądania: {response.status_code}")
                return False
        except requests.RequestException as e:
            # Obsługa błędów połączenia z serwerem
            log_event(f"Błąd połączenia (próba {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)  # Odczekaj przed kolejną próbą
            else:
                log_event("Wyczerpano limit prób połączenia.")
                return False

def play_music():
    """Włącza odtwarzanie muzyki."""
    if perform_request(f"{API_BASE_URL}player/play"):
        log_event("Muzyka została włączona.")

def stop_music():
    """Zatrzymuje odtwarzanie muzyki."""
    if perform_request(f"{API_BASE_URL}player/stop"):
        log_event("Muzyka została zatrzymana.")

# Logowanie konfiguracji
log_event("API URL base: " + API_BASE_URL)

# Harmonogram działań - codzienna aktywacja o określonych godzinach
schedule.every().day.at("09:00").do(play_music)  # Włączenie muzyki o 9:00
schedule.every().day.at("22:00").do(stop_music)  # Wyłączenie muzyki o 22:00

# Informacja o uruchomieniu harmonogramu
log_event("Harmonogram został uruchomiony. Skrypt działa w tle.")

# Główna pętla aplikacji - uruchamianie zadań zgodnie z harmonogramem
while True:
    schedule.run_pending()  # Wykonanie zaplanowanych zadań
    time.sleep(1)  # Krótka pauza, aby uniknąć nadmiernego obciążenia CPU
