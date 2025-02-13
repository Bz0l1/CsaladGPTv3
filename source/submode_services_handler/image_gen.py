import time

from openai import OpenAI
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from source.file_service_handler.file_reader import LocalFileReader
from source.file_service_handler.file_writer import LocalFileWriter

### KONSTANSOK ###
FILE_READER: LocalFileReader = LocalFileReader()
FILE_WRITER: LocalFileWriter = LocalFileWriter()
MAX_RETRIES: int = 2
TOKENS: tuple[str, str] = ("OPENAI_API_KEY", "GOOGLE_AI_API_KEY")
##################


class ImagenAPIs:
    def __init__(self) -> None:
        self.openai: OpenAI = OpenAI(api_key=FILE_READER.get_token(token_name=TOKENS[0]))
        self.gemini: genai.Client = genai.Client(api_key=FILE_READER.get_token(token_name=TOKENS[1]))

    def imagen_response(self, *, model: Optional[str], prompt: str):
        if model:
            if model == "imagen":
                try:
                    print(f"Prompt: {prompt}")
                    response = self.gemini.models.generate_images(
                        model="imagen-3.0-generate-002",
                        prompt=prompt,
                        config=types.GenerateImagesConfig(number_of_images=1)
                    )

                    for generated_image in response.generated_images:
                        image = Image.open(BytesIO(generated_image.image.image_bytes))
                        short_id: str = prompt[:10].replace(" ", "_")
                        current_date: str = time.strftime("%Y-%m-%d_%H-%M-%S")

                        try:
                            path: str = FILE_WRITER.path_generator(filename=f"{current_date}_{short_id}.png")
                            image.save(path)
                            print(f"Új kép: {path}")
                            return path
                        except Exception as err:
                            print(f"HIBA (ImagenAPIs.imagen_response): {err}")
                except Exception as err:
                    print(f"HIBA (ImagenAPIs.imagen_response): {err}")

if __name__ == '__main__':
    imagen = ImagenAPIs()
    imagen.imagen_response(model="imagen", prompt="romanian superhero, roman flag as cape, Captain romania")