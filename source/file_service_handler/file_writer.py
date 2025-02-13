from pathlib import Path
from typing import Any
import json

### KONSTANSOK ###
BASE_DIR: Path = Path(__file__).resolve().parent.parent
LOCAL_DB_PATH: Path = BASE_DIR / "database_service_handler" / "database"
FILENAMES: dict[str, str] = {
    "youtube_live_url": "youtube_live_url.txt",
    "ima_date_time": "ima_date_time.txt",
    "perc": "perc.txt",
    "roles": "roles.json",
    "javaslat": "javaslat.json",
}


###################

class LocalFileWriter:
    """
    A helyi fájlkezelő osztály.

    :argument: local_db_path: Path - A helyi adatbázis elérési útja.

    :function: _ensure_dir_exists - A fájlrendszer ellenőrzése.
    :function: _save_to_file - A fájlba írás.
    :function: save_youtube_live_url - Az élő stream URL-jének a mentése.
    :function: save_ima_date_time - Az ima időpontjának a mentése.
    :function: save_percek - Az ima percekének a mentése.
    """

    def __init__(self) -> None:
        self.local_db_path: Path = LOCAL_DB_PATH
        self._ensure_dir_exists()

    def _ensure_dir_exists(self) -> None:
        """
        A fájlrendszer ellenőrzése.

        :return:
        """
        self.local_db_path.mkdir(parents=True, exist_ok=True)

    def _save_to_file(self, *, filename: str, content: str) -> None:
        """
        A fájlba írás.

        :param filename: str - A fájl neve.
        :param content:  str - A fájl tartalma.
        :return:
        """
        try:
            file_path: Path = self.local_db_path / filename
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(str(content))
        except Exception as err:
            print(f"HIBA (file_writer.py): {err}")

    def save_youtube_live_url(self, *, content: str) -> None:
        """
        Az élő stream URL-jének a mentése.

        :param content: str - Az élő stream URL-je.
        :return:
        """
        self._save_to_file(filename=FILENAMES["youtube_live_url"], content=content)

    def save_ima_date_time(self, *, time: str) -> None:
        """
        Az ima időpontjának a mentése.

        :param time: str - Az ima időpontja.
        :return:
        """
        self._save_to_file(filename=FILENAMES["ima_date_time"], content=time)

    def save_percek(self, *, time: str) -> None:
        """
        Az ima percekének a mentése.

        :param time: str - Az ima percekének a száma.
        :return:
        """
        self._save_to_file(filename=FILENAMES["perc"], content=time)

    def save_json(self, *, filename: str, data: dict[Any, Any]) -> None:
        """
        JSON fájl mentése.

        :param filename: str - A fájl neve
        :param data: dict[Any, Any] - A fájl tartalma
        :return: None
        """
        try:
            file_path: Path = self.local_db_path / FILENAMES[filename]
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as err:
            print(f"HIBA (file_writer.py): {err}")

    def path_generator(self, *, filename: str) -> str:
        """
        A fájl elérési útjának a generálása.

        :param filename: str - A fájl neve.
        :return: str - A fájl elérési útja.
        """

        return str(self.local_db_path / filename)