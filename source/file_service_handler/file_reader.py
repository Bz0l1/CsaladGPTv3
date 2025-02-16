from fileinput import filename
from pathlib import Path
from typing import Optional

import discord
from dotenv import load_dotenv
from discord import File
import os
import json

### KONSTANSOK ###
load_dotenv()
BASE_DIR: Path = Path(__file__).resolve().parent.parent
LOCAL_DB_PATH: Path = BASE_DIR / "database_service_handler" / "database"


##################

class LocalFileReader:
    def __init__(self) -> None:
        self.local_db_path: Path = LOCAL_DB_PATH
        self._ensure_dir_exists()

    def _ensure_dir_exists(self) -> None:
        self.local_db_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_token(*, token_name: str) -> str:
        token: Optional[str] = os.getenv(token_name)

        if not token:
            raise ValueError(f"HIBA (file_reader.py): {token_name}")
        return token

    def read_json(self, *, file_name: str) -> dict:
        try:
            file_path: Path = self.local_db_path / f"{file_name}.json"

            with open(file_path, 'r', encoding="utf-8") as file:
                data: dict[str, str] = json.load(file)
                return data
        except FileNotFoundError:
            return {}

    def read_txt(self, *, file_name: str) -> str:
        try:
            file_path: Path = self.local_db_path / f"{file_name}.txt"

            with open(file_path, 'r', encoding="utf-8") as file:
                data: str = file.read()
                return data
        except FileNotFoundError:
            return ""

    def read_img(self, *, file_name: str) -> discord.File:
        try:
            file_path: Path = self.local_db_path / f"{file_name}.png"
            return File(str(file_path), filename=file_path.name)
        except FileNotFoundError:
            return File("")

    def get_alert(self):
        try:
            file_path: Path = self.local_db_path / "alert.gif"
            return File(str(file_path), filename=file_path.name)
        except FileNotFoundError:
            return File("")
