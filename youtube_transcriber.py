import os

from dotenv import load_dotenv
import googleapiclient.discovery
import googleapiclient.errors
from youtube_transcript_api import YouTubeTranscriptApi

channel_username = input('Enter Youtube channel username: ')
channel_id = input('Enter Youtube channel ID: ')
output_path = f'output/{channel_username}'
os.makedirs(output_path, exist_ok=True)

load_dotenv()
api_key = os.getenv('API_KEY')
if not api_key:
    print("Error: API key not found. Please ensure it's set in the .env file.")
    quit()

youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

# Get the ID of the channel's "Uploads" playlist
request = youtube.channels().list(
    part='contentDetails',
    id=channel_id
)

response = request.execute()

uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Get all video IDs from the "Uploads" playlist and fetch transcripts
video_ids = []
next_page_token = None

while True:
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=uploads_playlist_id,
        maxResults=50,
        pageToken=next_page_token
    )

    response = request.execute()

    for item in response['items']:
        video_id = item['contentDetails']['videoId']
        video_ids.append(video_id)

        # Fetch and save transcripts for each video
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript in transcript_list:
                transcript_data = transcript.fetch()
                language = transcript.language_code
                with open(f'{output_path}/{video_id}_{language}_transcript.txt', 'w') as f:
                    for line in transcript_data:
                        f.write(line['text'] + '\n')
        except Exception as e:
            print(f'Could not download transcripts for video {video_id}: {e}')

    next_page_token = response.get('nextPageToken')
    if next_page_token is None:
        break
