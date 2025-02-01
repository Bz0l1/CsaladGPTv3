from typing import Optional

from openai import OpenAI
from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type, retry

from source.file_service_handler.file_reader import LocalFileReader

### KONSTANSOK ###
FILE_READER: LocalFileReader = LocalFileReader()
BASE_PROMPT: str = "Csak és kizárólag magyarul válaszolj, kreatívan és röviden maximum 3 mondatban, "
MAX_RETRIES: int = 2
TOKEN_NAME: str = "OPENAI_API_KEY"


##################

class OpenAIAPI:
    """
    Az OpenAI API-t kezelő osztály.

    :argument: openai: OpenAI - Az OpenAI API objektuma.

    :function: text_response - A szöveg válasz generálása.
    """
    def __init__(self) -> None:
        self.openai: OpenAI = OpenAI(api_key=FILE_READER.get_token(token_name=TOKEN_NAME))

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
            response = self.openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"{BASE_PROMPT}{prompt}"},
                    {"role": "user", "content": prompt},
                ],
            )

            return response.choices[0].message.content
        except Exception as err:
            raise err
