from typing import Dict, Any, List


class Inventory:
    def __init__(self, data: Dict[str, Any]):
        self._inventory = {
            "items": {},
            "equipped": {}
        }
        items_list = data.get("items", [])
        for item_entry in items_list:
            for item_id, info in item_entry.items():
                self._inventory["items"][item_id] = info

        equipped_list = data.get("equipped", [])
        if equipped_list:
            self._inventory["equipped"] = equipped_list[0]
        else:
            self._inventory["equipped"] = None
        print(self._inventory)

    ### GETTERS ###
    @property
    def inventory(self) -> Dict[str, Any]:
        return self._inventory

    @property
    def items(self) -> Dict[str, Any]:
        return self._inventory["items"]

    @property
    def equipped(self) -> Dict[str, Any]:
        return self._inventory["equipped"]

    def get_item_by_id(self, *, item_id: str) -> Dict[str, Any]:
        return self._inventory["items"].get(item_id, {})

    def get_equipment_slots(self) -> Dict[str, Any]:
        return self._inventory["equipped"]

    ### ####### ###

    def add_item(self, *, item_id: str, amount: int) -> None:
        if item_id in self._inventory["items"]:
            self._inventory["items"][item_id]["amount"] += amount
        else:
            self._inventory["items"][item_id] = {"amount": amount}

    def equip_item(self, *, item_id: str, slot: str) -> bool:
        if item_id in self._inventory["items"]:
            if slot in self._inventory["equipped"]:
                self._inventory["equipped"][slot] = item_id
                return True
        return False

    def unequip_item(self, *, slot: str) -> None:
        if slot in self._inventory["equipped"]:
            self._inventory["equipped"][slot] = None

    def remove_item(self, *, item_id: str, amount: int) -> None:
        if item_id in self._inventory["items"]:
            self._inventory["items"][item_id]["amount"] -= amount
            if self._inventory["items"][item_id]["amount"] <= 0:
                del self._inventory["items"][item_id]


"""
{'items': [{'1': {'amount': 2}}], 'equipped': [{'head': None, 'body': '1', 'arms': None, 'legs': None, 'feet': None, 'accessory': None}]}
"""
