from pathlib import Path

from dotenv import load_dotenv
import os
import json

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
local_db_path = os.path.join(BASE_DIR, "database_service_handler", "local_database")

def get_token(token_name: str) -> str:
    token: str = os.getenv(token_name)

    if token is None:
        raise ValueError(f"HIBA (file_reader.get_token): {token_name} nem található!")

    return token


def read_json(file_name: str) -> dict:
    try:
        with open(f"{local_db_path}/{file_name}.json", "r", encoding="utf-8") as file:
            print(f"{file_name}.json sikeresen beolvasva")
            data: dict = json.load(file)
    except FileNotFoundError:
        data = {}

    return data

print(type(read_json("help")))

def read_txt(file_name: str) -> str:
    try:
        with open(f"{local_db_path}/{file_name}.txt", "r", encoding="utf-8") as file:
            print(f"{file_name}.txt sikeresen beolvasva")
            data: str = file.read()
    except FileNotFoundError:
        data = ""

    return data