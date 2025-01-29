import random
from source.file_service_handler.file_reader import read_json


def read_bible(lang: str | None = None) -> (str, str):
    books: dict = {
        "hu": "karoli",
        "en": "bishops",
        "jp": "kougo",
        "es": "rvg",
    }

    if lang is None:
        lang = random.choice(list(books.keys()))
        book: str = books[lang]
    else:
        book = books[lang]

    data: dict = read_json(book)
    if data == {}:
        return "Hiba történt a fájl beolvasásakor."

    selected_verse: dict = random.choice(data["verses"])
    verse_text: str = (f"{selected_verse['book_name']} {selected_verse['chapter']}: "
                       f"{selected_verse['verse']} - {selected_verse['text']}")
    return verse_text, lang