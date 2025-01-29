import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from source.file_service_handler.file_reader import get_token, read_txt
from source.file_service_handler.file_writer import save_youtube_live_url

def is_channel_live(*, is_command: bool) -> str | None:
    if not is_command:
        saved_data: str = read_txt("youtube_live_url")
        saved_time, saved_url = None, None

        if saved_data != "":
            try:
                saved_time_str, saved_url = saved_data.split("--", 1)
                saved_time = float(saved_time_str)
            except ValueError:
                saved_time, saved_url = None, None

        if saved_time is not None and (time.time() - saved_time) < 25200:
            return None

    channel_id = get_token("YOUTUBE_TEST_CHANNEL_ID")
    api_key = get_token("YOUTUBE_API_KEY")

    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            eventType='live',
            type='video',
            maxResults=1
        )
        response = request.execute()

        if not response.get('items'):
            return None

        live_video_id = response['items'][0]['id']['videoId']
        live_url = f"https://www.youtube.com/watch?v={live_video_id}"

        if not is_command and saved_url == live_url:
            return None

        save_youtube_live_url(content=f"{time.time()}--{live_url}")
        return live_url

    except HttpError as e:
        print(f'HTTP Error {e.resp.status}: {e._get_reason()}')
        return None
    except Exception as e:
        print(f'Unexpected error: {e}')
        return None