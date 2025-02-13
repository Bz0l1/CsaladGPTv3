import random
from typing import Optional

from source.file_service_handler.file_reader import LocalFileReader

######### KONSTANSOK #########
BOOKS: dict[str, str] = {
    "hu": "karoli",
    "en": "bishops",
    "jp": "kougo",
    "es": "rvg",
}

FILE_READER: LocalFileReader = LocalFileReader()


##############################

class BibleVerse:
    """
    A Biblia idézetét tároló osztály.

    :argument data_books: dict[str, str] - A Biblia könyveinek a nevei és a hozzájuk tartozó fájlok.
    :argument lang: str - A Biblia nyelve.

    :function: read_bible - A Biblia olvasása.
    """

    def __init__(self, *, lang: Optional[str] = None):
        self.data_books: dict[str, str] = BOOKS
        self.lang: str = lang if lang else random.choice(list(self.data_books.keys()))

    def read_bible(self) -> (str, str):
        """
        A Biblia olvasása.

        :return: tuple[str, str] - Az idézet és a nyelv.
        """
        data: dict[str, str] = FILE_READER.read_json(file_name=self.data_books[self.lang])
        if data == {}:
            return "HIBA", self.lang

        selected_verse: dict[str, str] = random.choice(data["verses"])
        verse_text: str = (f"{selected_verse['book_name']} {selected_verse['chapter']}: "
                           f"{selected_verse['verse']} - {selected_verse['text']}")
        return verse_text, self.lang
