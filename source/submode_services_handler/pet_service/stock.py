from typing import Dict, Any

class Stock:
    def __init__(self, data: Dict[str, Any]):
        pass

"""
self._stock: Dict = {
            "portfolio": {},
        }
        for stock_entry in data["stock"]["portfolio"]:
            for id, info in stock_entry.items():
                self._stock["portfolio"][id] = info
"""