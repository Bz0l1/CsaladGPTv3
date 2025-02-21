from typing import Dict, Tuple, Any, Optional

from openai import OpenAI
import google.generativeai as genai
from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type, retry

from source.file_service_handler.file_reader import LocalFileReader

### KONSTANSOK ###
FILE_READER: LocalFileReader = LocalFileReader()
SETTINGS: str = "FONTOS DOLGOK: Ne legyél túl mesebeli, ne legyél irreleváns. Úgy beszélj erről a scenario-ról, mintha egy valós eseményről lenne szó. A történetnek humorosnak kell lennie, de ne legyen erőltetett vicces. A történetnek egyértelműen és érthetően kell lezajlania, ne legyenek benne homályos vagy 'értelmetlen' részek. Ne használj jelzőket Selchris-re (pl: Selchris, a lelkes, de kissé amatőr DJ vagy Selchris, a híres DJ), csak a történetre koncentrálj. A történet mindig kezdődjön így: 'Selchris..."
BASE_PROMPT_1: str = "Csak és kizárólag magyarul válaszolj, kreatívan és röviden maximum 4 mondatban. A szereped: Te egy narrátor vagy. Az egyetlen feladatod, hogy kitalálj egy humorosnak szánt scenario-t egy DJ-ről, akit Selchris-nek hívnak. A válaszodnak ezen az alap forgatókönyvön kell alapulnia: "
BASE_PROMPT_1_continue: str = " A történet kimenetelének van egy nagyon súlyos befolyásoló tényezője, mennyire volt sikeres Selchris az adott scenario-ban. Ezt vedd figyelembe a válaszodban. Ha sikerült akkor happy ending van. Ha nem, akkor nagyon vagy nagyon kínos, vagy nagyon szomorú a vége"
BONUS: str = "A történet folyamán selchris vagy kap/talál egy tárgyat vagy elveszít egy tárgyat. Ezt ágyazd be a történetbe."
MAX_RETRIES: int = 2
TOKENS: Tuple[str] = ("OPENAI_API_KEY",)
TYPES_ROLES: Dict[str, Any] = {
    "work": {
        "type": {
            "dj": ["Alap: DJ munka,", "Leírás: Selchris elválalt egy DJ munkát."],
            "side_job": ["Alap: Mellékállás",
                         "Leírás: Selchris elvállalt egy mellékállást aminek semmi köze a DJ munkájához (ezt ne említsd)."],
        }
    }
}


##################

class PetAI:
    def __init__(self) -> None:
        self.openai: OpenAI = OpenAI(api_key=FILE_READER.get_token(token_name=TOKENS[0]))

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
        retry_error_callback=lambda retry_state: f"Nem sikerült válaszolni.\n||{retry_state.outcome.exception()}||"
    )
    def text_response(self, *, type: str, sub_type: Optional[str] = None, success: bool, got_item: Optional[str],
                 lost_item: Optional[str], amount: Optional[int]) -> str:
        try:
            if type in ["work"]:
                instruction: str = f"{BASE_PROMPT_1} {SETTINGS} {BONUS}"

                if got_item or lost_item:
                    bonus: str = f"megszerzett tárgy: {got_item} {amount} darab" if got_item else f"elveszített tárgy: {lost_item} {amount} darab"
                else:
                    bonus = ""

                content: str = f"{TYPES_ROLES[type]['type'][sub_type][0]} {TYPES_ROLES[type]['type'][sub_type][1]} {BASE_PROMPT_1_continue} Sikeresség: {'sikeres' if success else 'sikertelen'} {bonus}"
                print(instruction)
                print(content)

            response = self.openai.chat.completions.create(
                model="o3-mini",
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user",
                     "content": f"{content}"},
                ],
            )

            return response.choices[0].message.content

        except Exception as err:
            raise err
