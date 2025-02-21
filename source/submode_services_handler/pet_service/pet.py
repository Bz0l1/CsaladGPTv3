from typing import Dict, List, Optional
import datetime
import random

from inventory import Inventory
from stock import Stock

from source.file_service_handler.file_writer import LocalFileWriter
from source.file_service_handler.file_reader import LocalFileReader
from source.submode_services_handler.pet_service.handlers.pet_ai import PetAI

### KONSTANSOK ###
PET_FILE: str = "pet"
FILE_WRITER: LocalFileWriter = LocalFileWriter()
FILE_READER: LocalFileReader = LocalFileReader()
PET_AI: PetAI = PetAI()


### ############ ###

# TODO MINDEN IS
class Pet:
    def __init__(self, *, discord_user_id: str, user_name: str) -> None:
        data: Dict = self.load_data(user_id=discord_user_id, user_name=user_name)

        self._dc_id: str = data["dc_id"]
        self._dc_name: str = data["dc_name"]
        self._age: int = data["age_days"]
        self._money: int = data["money"]
        self._energy: int = data["energy"]
        self._mood: int = data["mood"]
        self._hunger: int = data["hunger"]
        self._thirst: int = data["thirst"]
        self._hygiene: int = data["hygiene"]
        self._friends: List = data["friends"]
        self._lonely: int = data["lonely"]

        self._inventory: Inventory = Inventory(data["inventory"])
        self._stock: Stock = Stock(data["stock"])

        self._last_update: datetime.datetime = self.parse_datetime(data["last_update"])
        self._last_interaction: datetime.datetime = self.parse_datetime(data["last_interaction"])

        self._daily_limits: Dict = data["daily_limits"]
        self._current_mission: str = data["current_mission_id"]
        self._completed_missions: List = data["completed_mission_ids"]
        self._achievements: List = data["achievements"]
        self._effects: List = data["effects"]
        self._last_action: str = data["last_action"]
        self._is_afk: bool = data["is_afk"]
        self._afk_duration: int = data["afk_duration"]
        self._afk_start: datetime.datetime = self.parse_datetime(data["afk_start"]) if data["afk_start"] else None
        self._is_dead: bool = data["is_dead"]

    ### Getters ###

    @property
    def age(self) -> int:
        return self._age

    @property
    def money(self) -> int:
        return self._money

    @property
    def energy(self) -> int:
        return self._energy

    @property
    def mood(self) -> int:
        return self._mood

    @property
    def hunger(self) -> int:
        return self._hunger

    @property
    def thirst(self) -> int:
        return self._thirst

    @property
    def hygiene(self) -> int:
        return self._hygiene

    @property
    def friends(self) -> List:
        return self._friends

    @property
    def lonely(self) -> int:
        return self._lonely

    @property
    def last_update(self) -> datetime.datetime:
        return self._last_update

    @property
    def last_interaction(self) -> datetime.datetime:
        return self._last_interaction

    @property
    def daily_limits(self) -> Dict:
        return self._daily_limits

    @property
    def current_mission(self) -> str:
        return self._current_mission

    @property
    def completed_missions(self) -> List:
        return self._completed_missions

    @property
    def achievements(self) -> List:
        return self._achievements

    @property
    def effects(self) -> List:
        return self._effects

    @property
    def last_action(self) -> str:
        return self._last_action

    @property
    def is_afk(self) -> bool:
        return self._is_afk

    @property
    def afk_duration(self) -> int:
        return self._afk_duration

    @property
    def afk_start(self) -> datetime.datetime:
        return self._afk_start

    @property
    def is_dead(self) -> bool:
        return self._is_dead

    @property
    def inventory(self) -> Inventory:
        return self._inventory

    @property
    def stock(self) -> Stock:
        return self._stock

    ### ####### ###

    ### Setters ###
    @age.setter
    def age(self, value: int) -> None:
        self._age = value

    @money.setter
    def money(self, value: int) -> None:
        if self.money - value < 0:
            self._money = 0

    @energy.setter
    def energy(self, value: int) -> None:
        if self.energy - value < 0:
            self._energy = 0

        if self.energy + value > 100:
            self._energy = 100

    @mood.setter
    def mood(self, value: int) -> None:
        if self.mood - value < 0:
            self._mood = 0

        if self.mood + value > 100:
            self._mood = 100

    @hunger.setter
    def hunger(self, value: int) -> None:
        if self.hunger - value < 0:
            self._hunger = 0

        if self.hunger + value > 100:
            self._hunger = 100

    @thirst.setter
    def thirst(self, value: int) -> None:
        if self.thirst - value < 0:
            self._thirst = 0

        if self.thirst + value > 100:
            self._thirst = 100

    @hygiene.setter
    def hygiene(self, value: int) -> None:
        if self.hygiene - value < 0:
            self._hygiene = 0

        if self.hygiene + value > 100:
            self._hygiene = 100

    @lonely.setter
    def lonely(self, value: int) -> None:
        if self.lonely - value < 0:
            self._lonely = 0

        if self.lonely + value > 100:
            self._lonely = 100

    @last_update.setter
    def last_update(self, value: datetime.datetime) -> None:
        self._last_update = value

    @last_interaction.setter
    def last_interaction(self, value: datetime.datetime) -> None:
        self._last_interaction = value

    @last_action.setter
    def last_action(self, value: str) -> None:
        self._last_action = value

    @is_afk.setter
    def is_afk(self, value: bool) -> None:
        self._is_afk = value

    @afk_duration.setter
    def afk_duration(self, value: int) -> None:
        self._afk_duration = value

    @afk_start.setter
    def afk_start(self, value: datetime.datetime) -> None:
        self._afk_start = value

    @is_dead.setter
    def is_dead(self, value: bool) -> None:
        self._is_dead = value

    ### ####### ###

    def add_effect(self, *, effect: str) -> None:
        self._effects.append(effect)

    def remove_effect(self, *, effect: str) -> None:
        self._effects.remove(effect)

    def add_friend(self, *, friend: str) -> None:
        self._friends.append(friend)

    def remove_friend(self, *, friend: str) -> None:
        self._friends.remove(friend)

    def add_completed_mission(self, *, mission: str) -> None:
        self._completed_missions.append(mission)

    def add_acievement(self, *, achievement: str) -> None:
        self._achievements.append(achievement)

    def modify_daily_limit(self, *, key: str, limit: int) -> None:
        self._daily_limits[key] = limit

    ##############################

    @staticmethod
    def _get_modifier(*, x: int, L: int, U: int, MN: float, MP: float, is_positive: bool) -> float:
        """
        A dolgok sikerességét eldöntő mindenség

        :param x: int - az adott stat értéke (energy, mood, hygiene, hunger, thirst, lonely)
        :param L: int - az alsó határ - ha x < L, akkor a modifier +
        :param U: int - a felső határ - ha x > U, akkor a modifier -
        :param MN: float - negatív hatás mértéke (0 és 1 között) - ha x < L vagy x > U
        :param MP: float - pozitív hatás mértéke (0 és 1 között) - ha L ≤ x ≤ U
        :param is_positive: bool - True, ha a stat pozitív hatással van a cselekvésre, False, ha negatív hatással van.

        :return: float - a modifier értéke (-1 és 1 között) - ha x < L, akkor -MN, ha x > U, akkor +MN, egyébként 0
        """

        if is_positive:  # energy, mood, hygiene
            if x < L:
                return -MN * (1 - x / L)  # x=0 → -MN, x=L → 0
            elif x > U:
                return MP * (x - U) / (100 - U)  # x=U → 0, x=100 → MP
            else:
                return 0  # L ≤ x ≤ U
        else:  # hunger, thirst, lonely
            if x < L:
                return MP * (L - x) / L  # x=0 → +MP, x=L → 0
            elif x > U:
                return -MN * (x - U) / (100 - U)  # x=U → 0, x=100 → -MN
            else:
                return 0  # L ≤ x ≤ U

    def rnd(self, *, starting_chance: float) -> bool:
        """
        RnD rendszer az akciók sikerességéhez

        :param starting_chance: float - az alap esély (0 és 1 között)

        :return: bool - True, ha jó, False, ha nem
        """
        total_modifier: float = 0.0

        total_modifier += self._get_modifier(x=self._energy, L=50, U=90, MN=0.2, MP=0.1,
                                             is_positive=True)  # energy; 50-90
        total_modifier += self._get_modifier(x=self._mood, L=20, U=70, MN=0.3, MP=0.15, is_positive=True)  # mood; 20-70
        total_modifier += self._get_modifier(x=self._hygiene, L=30, U=70, MN=0.25, MP=0.1,
                                             is_positive=True)  # hygiene; 30-70

        total_modifier += self._get_modifier(x=self._hunger, L=30, U=70, MN=0.2, MP=0.1,
                                             is_positive=False)  # hunger; 30-70
        total_modifier += self._get_modifier(x=self._thirst, L=30, U=70, MN=0.2, MP=0.1,
                                             is_positive=False)  # thirst; 30-70
        total_modifier += self._get_modifier(x=self._lonely, L=30, U=70, MN=0.15, MP=0.05,
                                             is_positive=False)  # lonely; 30-70

        final_chance = max(0.0, min(1.0,
                                    starting_chance + total_modifier))  # 0 ≤ final_chance ≤ 1; ha < 0, akkor 0, ha > 1, akkor 1
        return random.random() < final_chance

    def work(self, *, type: str) -> Dict:
        outcome: Dict = {}

        if type == "dj":
            base_chance: float = 0.5
            success: bool = self.rnd(starting_chance=base_chance)

            if success:
                money: int = random.randint(1200, 1600)
                energy: int = -(random.randint(10, 20))
                mood: int = -(random.randint(5, 10))
                lonely: int = random.randint(2, 5)
                hunger: int = random.randint(2, 10)
                thirst: int = random.randint(2, 10)
                hygiene: int = -(random.randint(5, 10))
                dj_set: int = -(random.randint(1, 5))
            else:
                money: int = random.randint(200, 350)
                energy: int = -(random.randint(15, 30))
                mood: int = -(random.randint(10, 20))
                lonely: int = random.randint(5, 10)
                hunger: int = random.randint(2, 10)
                thirst: int = random.randint(2, 10)
                hygiene: int = -(random.randint(5, 10))
                dj_set: int = -(random.randint(3, 10))
        else:
            base_chance: float = 0.3
            success: bool = self.rnd(starting_chance=base_chance)

            if success:
                money: int = random.randint(200, 500)
                energy: int = -(random.randint(10, 20))
                mood: int = -(random.randint(5, 10))
                lonely: int = random.randint(2, 5)
                hunger: int = random.randint(2, 10)
                thirst: int = random.randint(2, 10)
                hygiene: int = -(random.randint(5, 10))

            else:
                money: int = random.randint(50, 150)
                energy: int = -(random.randint(15, 30))
                mood: int = -(random.randint(10, 20))
                lonely: int = random.randint(5, 10)
                hunger: int = random.randint(2, 10)
                thirst: int = random.randint(2, 10)
                hygiene: int = -(random.randint(5, 10))

        outcome["money"] = money
        outcome["energy"] = energy
        outcome["mood"] = mood
        outcome["lonely"] = lonely
        outcome["hunger"] = hunger
        outcome["thirst"] = thirst
        outcome["hygiene"] = hygiene
        outcome["dj_set"] = dj_set if type == "dj" else None

        self.money += money
        self.energy += energy
        self.mood += mood
        self.lonely += lonely
        self.hunger += hunger
        self.thirst += thirst
        self.hygiene += hygiene
        self.last_action = "work"
        self.last_interaction = datetime.datetime.now()
        self.last_update = datetime.datetime.now()

        petai: PetAI = PetAI()

        message: str = petai.text_response(type="work", sub_type="dj" if type == "dj" else "side_job", success=success, got_item=None, lost_item=None, amount=None)
        self.save(data=self.rebuild_dict())
        return {
            "success": success,
            "outcome": outcome,
            "message": message
        }

    def party(self) -> Dict:
        pass

    def sleep(self) -> Dict:
        pass

    def relax(self) -> Dict:
        pass

    def status(self) -> Dict:
        pass

    def steal(self) -> Dict:
        pass

    def repair(self) -> Dict:
        pass

    def afk(self) -> None:
        pass

    def die(self) -> None:
        pass

    def clean(self) -> Dict:
        pass

    def shop(self) -> Dict:
        pass

    def buy(self) -> None:
        pass

    def sell(self) -> None:
        pass

    def eat(self) -> None:
        pass

    def drink(self) -> None:
        pass

    def use(self) -> None:
        pass

    def drop(self) -> None:
        pass

    def equip(self) -> None:
        pass

    def unequip(self) -> None:
        pass

    def invest(self) -> None:
        pass

    def withdraw_from_stock(self) -> None:
        pass

    def deposit_to_bank(self) -> None:
        pass

    def withdraw_from_bank(self) -> None:
        pass

    def transfer(self) -> None:
        pass

    def save(self, *, data: Optional[Dict] = None) -> None:
        all_data: Dict = FILE_READER.read_json(file_name=PET_FILE)
        if not all_data:
            all_data = {}

        date_format: str = "%Y-%m-%d %H:%M:%S"

        if data:
            all_data[data["dc_id"]] = data
        else:
            compiler: Dict = {
                "dc_id": self._dc_id,
                "dc_name": self._dc_name,
                "age_days": self._age,
                "money": self._money,
                "energy": self._energy,
                "mood": self._mood,
                "hunger": self._hunger,
                "thirst": self._thirst,
                "hygiene": self._hygiene,
                "friends": self._friends,
                "lonely": self._lonely,
                "inventory": self._inventory.get_in_dict(),
                "stock": self._stock.get_in_dict(),
                "last_update": self._last_update.strftime(date_format),
                "last_interaction": self._last_interaction.strftime(date_format),
                "daily_limits": self._daily_limits,
                "current_mission": self._current_mission,
                "completed_missions": self._completed_missions,
                "achievements": self._achievements,
                "effects": self._effects,
                "last_action": self._last_action,
                "is_afk": self._is_afk,
                "afk_duration": self._afk_duration,
                "afk_start": self._afk_start.strftime(date_format) if self._afk_start else None,
                "is_dead": self._is_dead
            }

            all_data[self._dc_id] = compiler
        FILE_WRITER.save_json(filename=PET_FILE, data=all_data)

    def generate_pet(self, *, user_id: str, user_name: str) -> Dict:
        data: Dict = {
            "dc_id": user_id,
            "dc_name": user_name,
            "age_days": 1,
            "money": 1500,
            "energy": 100,
            "mood": 100,
            "hunger": 100,
            "thirst": 100,
            "hygiene": 100,
            "friends": [],
            "lonely": 0,
            "inventory": {
                "items": [],
                "equipped": {
                    "head": "",
                    "body": "",
                    "arms": "",
                    "legs": "",
                    "feet": "",
                    "accessory": ""
                }
            },
            "stock": {
                "portfolio": [],
            },
            "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_interaction": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "daily_limits": {
                "work": 3,
                "sleep": 2,
                "relax": 2,
                "party": 1,
                "steal": 2,
                "bath": 2
            },
            "current_mission_id": "",
            "completed_mission_ids": [],
            "achievements": [],
            "effects": [],
            "last_action": "",
            "is_afk": False,
            "afk_duration": 0,
            "afk_start": None,
            "is_dead": False
        }

        self.save(data=data)
        return data

    def rebuild_dict(self) -> Dict:
        return {
            "dc_id": self._dc_id,
            "dc_name": self._dc_name,
            "age_days": self._age,
            "money": self._money,
            "energy": self._energy,
            "mood": self._mood,
            "hunger": self._hunger,
            "thirst": self._thirst,
            "hygiene": self._hygiene,
            "friends": self._friends,
            "lonely": self._lonely,
            "inventory": self._inventory.get_in_dict(),
            "stock": self._stock.get_in_dict(),
            "last_update": self._last_update.strftime("%Y-%m-%d %H:%M:%S"),
            "last_interaction": self._last_interaction.strftime("%Y-%m-%d %H:%M:%S"),
            "daily_limits": self._daily_limits,
            "current_mission": self._current_mission,
            "completed_missions": self._completed_missions,
            "achievements": self._achievements,
            "effects": self._effects,
            "last_action": self._last_action,
            "is_afk": self._is_afk,
            "afk_duration": self._afk_duration,
            "afk_start": self._afk_start.strftime("%Y-%m-%d %H:%M:%S") if self._afk_start else None,
            "is_dead": self._is_dead
        }

    def load_data(self, *, user_id: str, user_name: str) -> Dict:
        all_data: Dict = FILE_READER.read_json(file_name=PET_FILE)
        if not all_data:
            all_data = {}

        if user_id not in all_data:
            new_pet_data = self.generate_pet(user_id=user_id, user_name=user_name)
            all_data[user_id] = new_pet_data
            FILE_WRITER.save_json(filename=PET_FILE, data=all_data)

        return all_data[user_id]

    @staticmethod
    def load_every_pet() -> Dict:
        all_data: Dict = FILE_READER.read_json(file_name=PET_FILE)
        if not all_data:
            all_data = {}
        return all_data

    @staticmethod
    def parse_datetime(dt_str: Optional[str]) -> datetime.datetime:
        if not dt_str:
            return datetime.datetime.now()
        try:
            return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.datetime.strptime(dt_str, "%Y-%m-%d-%H:%M:%S")


def register(*, user_id: str, user_name: str) -> Dict:
    return Pet(discord_user_id=user_id, user_name=user_name).generate_pet(user_id=user_id, user_name=user_name)


if __name__ == '__main__':
    id: str = "696657530537115669"
    name: str = "__z0l1__"

    pet: Pet = Pet(discord_user_id=id, user_name=name)

    print(pet.money)
    print(pet.energy)
    print(pet.mood)
    print(pet.hunger)
    print(pet.thirst)
    print(pet.hygiene)

    print("-" * 50 + "\n" + "-" * 50)

    print(pet.work(type="dj"))
    print("-" * 50)
    print(pet.money)
    print(pet.energy)
    print(pet.mood)
    print(pet.hunger)
    print(pet.thirst)
    print(pet.hygiene)

    print("-" * 50 + "\n" + "-" * 50 + "\n" + "-" * 50)

    print(pet.work(type="work"))
    print("-" * 50)
    print(pet.money)
    print(pet.energy)
    print(pet.mood)
    print(pet.hunger)
    print(pet.thirst)
    print(pet.hygiene)

    print("-" * 50 + "\n" + "-" * 50 + "\n" + "-" * 50)
