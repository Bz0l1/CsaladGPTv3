from typing import Optional

from openai import OpenAI
import google.generativeai as genai
from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type, retry

from source.file_service_handler.file_reader import LocalFileReader

### KONSTANSOK ###
FILE_READER: LocalFileReader = LocalFileReader()
BASE_PROMPT: str = "Csak és kizárólag magyarul válaszolj, kreatívan és röviden maximum 3 mondatban. A szereped: "
MAX_RETRIES: int = 2
TOKENS: tuple[str, str] = ("OPENAI_API_KEY", "GOOGLE_AI_API_KEY")


##################

class AIChatAPIs:
    """
    Az OpenAI API-t kezelő osztály.

    :argument: openai: OpenAI - Az OpenAI API objektuma.

    :function: text_response - A szöveg válasz generálása.
    """

    def __init__(self) -> None:
        self.openai: OpenAI = OpenAI(api_key=FILE_READER.get_token(token_name=TOKENS[0]))
        genai.configure(api_key=FILE_READER.get_token(token_name=TOKENS[1]))
        self.roles: dict = FILE_READER.read_json(file_name="roles")

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
        retry_error_callback=lambda retry_state: f"Nem sikerült válaszolni.\n||{retry_state.outcome.exception()}||"
    )
    async def text_response(self, *, prompt: str, role: Optional[str] = None, memory: Optional[str] = None,
                            model: str = "gpt-4o-mini") -> str:
        """
        Szöveges válasz generálása.

        :param prompt: str - user prompt
        :param role: str - user role
        :param memory: str - ha van privát chat todo: privát chat implementálása
        :param model: str - a model neve (default: gpt-4o-mini) todo: model választás implementálása (xp)
        :return: str - a válasz
        """
        try:
            if model == "gpt-4o-mini" or model == "o3-mini":
                response = self.openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": f"{BASE_PROMPT}{self.get_role(role=role) if role else "Nincs"}"},
                        {"role": "user", "content": prompt},
                    ],
                )

                return response.choices[0].message.content
            elif model == "gemini-1.5-flash":
                gemini: genai.GenerativeModel = genai.GenerativeModel(model)
                instruction: str = f"{BASE_PROMPT}{self.get_role(role=role) if role else 'Nincs'} Az üzenet: {prompt}"
                response = gemini.generate_content(instruction)
                return response.text

        except Exception as err:
            raise err

    def get_role(self, *, role: str) -> dict:
        return self.roles[role]["prompt"]

