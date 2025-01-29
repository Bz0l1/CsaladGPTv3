import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
local_db_path = os.path.join(BASE_DIR, "database_service_handler", "database")

def save_youtube_live_url(content: str):
    with open(f"{local_db_path}/youtube_live_url.txt", "w", encoding="utf-8") as file:
        file.write(content)

def save_ima_date_time(time: str) -> None:
    with open(f"{local_db_path}/ima_date_time.txt", "w", encoding="utf-8") as file:
        file.write(time)

def save_percek(time: str) -> None:
    with open(f"{local_db_path}/perc.txt", "w", encoding="utf-8") as file:
        file.write(time)