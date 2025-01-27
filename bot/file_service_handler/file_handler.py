from dotenv import load_dotenv
import os

def get_token(token_name: str) -> str:
    load_dotenv()
    token: str = os.getenv(token_name)

    if token is None:
        raise ValueError(f"HIBA (get_token): {token_name} nem található")

    return token