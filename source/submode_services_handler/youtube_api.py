import time
from dataclasses import dataclass

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing_extensions import Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from source.file_service_handler.file_reader import LocalFileReader
from source.file_service_handler.file_writer import LocalFileWriter

######### KONSTANSOK #########
TIME: int = 25200  # 7 óra
MAX_RETRIES: int = 3
FILE: str = "youtube_live_url"
TOKENS: tuple[str, str] = ("YOUTUBE_CHANNEL_ID", "YOUTUBE_API_KEY")
FILE_READER: LocalFileReader = LocalFileReader()
FILE_WRITER: LocalFileWriter = LocalFileWriter()


##############################


@dataclass
class LiveStreamStatus:
    """
    Az élő stream státuszát tároló osztály.

    :argument url: Optional[str] - Az élő stream URL-je.
    :argument is_new: bool - Az érték, hogy új-e az élő stream.
    :argument cached: bool - Az érték, hogy a stream URL-je cache-elve van-e.
    """

    url: Optional[str]
    is_new: bool
    cached: bool


class YoutubeAPI:
    """
    A YouTube API-t kezelő osztály.

    :argument: channel_id: str - A YouTube csatorna ID-je.
    :argument: api_key: str - A YouTube API kulcsa.
    :argument: youtube: googleapiclient.discovery.Resource - A YouTube API objektuma.

    :function: fetch_live_stream - Az élő stream lekérdezése.
    :function: _stream_parser - Az élő stream URL-jének a kinyerése a YouTube API válaszából.
    """

    def __init__(self):
        self.channel_id = FILE_READER.get_token(token_name=TOKENS[0])
        self.api_key = FILE_READER.get_token(token_name=TOKENS[1])
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HttpError, TimeoutError)),
    )
    def fetch_live_stream(self) -> Optional[str]:
        """
        Az élő stream lekérdezése.
        @retry: Az API hívás újrapróbálkozása hiba esetén: 3 próbálkozás, exponenciális várakozás 4 és 10 másodperc között.

        :return: Optional[str] - Az élő stream URL-je, ha van, egyébként None.
        """

        request: dict = self.youtube.search().list(
            part='snippet',
            channelId=self.channel_id,
            eventType='live',
            type='video',
            maxResults=1
        )
        response: dict = request.execute()
        return self._stream_parser(response=response)

    def _stream_parser(self, *, response: dict) -> Optional[str]:
        """
        Az élő stream URL-jének a kinyerése a YouTube API válaszából.

        :param response: dict - A YouTube API válasza.
        :return: Optional[str] - Az élő stream URL-je, ha van, egyébként None.
        """

        if not response.get('items'):
            return None

        try:
            return f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
        except KeyError:
            return None


class CacheHandler:
    """
    A cache-elt adatokat kezelő osztály.
    chache: Az adatokat tartalmazó fájl neve.

    :function: read_chache - A cache-elt adatok beolvasása.
    :function: is_valid - Az adatok érvényességének az ellenőrzése.
    :function: update_url - Az élő stream URL-jének a frissítése.
    """

    @staticmethod
    def read_chache() -> Tuple[Optional[float], Optional[str]]:
        """
        A fájlból beolvassa a tárolt adatokat.

        :return: Tuple[Optional[float], Optional[str]] - A cache-elt időbélyeg és az élő stream URL-je. Ha nincs adat, akkor None.
        """

        data: str = FILE_READER.read_txt(file_name=FILE)
        print(data)

        if not data:
            return None, None

        try:
            timestamp, url = data.split("--", 1)
            return float(timestamp), url
        except ValueError:
            return None, None

    @staticmethod
    def is_valid(*, cached_time: Optional[float]) -> bool:
        """
        Az adatok validálása.

        :param cached_time:  Optional[float] - A cache-elt időbélyeg.
        :return:
        """
        return cached_time and (time.time() - cached_time) < TIME

    @staticmethod
    def update_url(*, url: str) -> None:
        """
        Az élő stream URL-jének a frissítése.
        fájl: FILE (youtube_live_url)
        :param url: str - Az élő stream URL-je.
        :return:
        """

        FILE_WRITER.save_youtube_live_url(content=f"{time.time()}--{url}")


def check_channel_status(*, is_command: bool) -> LiveStreamStatus:
    """
    A fő metódus, ami az élő stream státuszát ellenőrzi.
    Itt történik a cache-elt adatok beolvasása, az API hívás, az adatok frissítése és a válasz visszaadása.

    :param is_command: bool - Az érték, hogy parancsban lett-e lekérdezve.
    :return: LiveStreamStatus - Az élő stream státusza.
    """

    cached_time, cached_url = CacheHandler.read_chache()

    if not is_command and CacheHandler.is_valid(cached_time=cached_time):
        return LiveStreamStatus(url=cached_url, is_new=False, cached=True)

    try:
        youtube: YoutubeAPI = YoutubeAPI()
        live_url: Optional[str] = youtube.fetch_live_stream()

        if live_url and (is_command or live_url != cached_url):
            CacheHandler.update_url(url=live_url)
            return LiveStreamStatus(url=live_url, is_new=False, cached=False)

        return LiveStreamStatus(url=live_url, is_new=False, cached=True)

    except HttpError as err:
        print(f"HIBA (youtube_api.py): {err}")
        return LiveStreamStatus(url=cached_url, is_new=False, cached=True)
    except Exception as err:
        print(f"HIBA (youtube_api.py): {err}")
        raise
