from typing import Dict

from source.file_service_handler.file_reader import LocalFileReader

### KONSTANSOK ###
FILE_READER: LocalFileReader = LocalFileReader()

##################


ITEMS: Dict = FILE_READER.read_json(file_name="items")


def get_item_by_id(item_id: str) -> Dict:
    return ITEMS.get(item_id, {})


def get_items() -> Dict:
    return ITEMS


def get_item_name(item_id: str) -> str:
    return get_item_by_id(item_id).get("name", "")


def get_item_type(item_id: str) -> str:
    return get_item_by_id(item_id).get("type", "")


def get_item_description(item_id: str) -> str:
    return get_item_by_id(item_id).get("description", "")


def get_item_price(item_id: str) -> int:
    return get_item_by_id(item_id).get("price", 0)


def get_item_rarity(item_id: str) -> float:
    return get_item_by_id(item_id).get("rarity", 0.0)


def get_item_effects(item_id: str) -> Dict:
    return get_item_by_id(item_id).get("effects", {})
