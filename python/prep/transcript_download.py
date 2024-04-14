''' Started with: https://github.com/gloveboxes/Semantic-Search-with-OpenAI-Embeddings-and-Functions/blob/main/prep/transcript_download.py '''
''' This script downloads the transcripts for all the videos in a YouTube playlist. '''

import os
import sys
import json
import time
import threading
import argparse
import queue
import googleapiclient.discovery
import googleapiclient.errors
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter
from dotenv import load_dotenv
load_dotenv()

GOOGLE_DEVELOPER_API_KEY = os.getenv('GOOGLE_DEVELOPER_API_KEY')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')
TRANSCRIPT_FOLDER = os.getenv('TRANSCRIPT_FOLDER')

# Initialize the Google developer API client
GOOGLE_API_SERVICE_NAME = "youtube"
GOOGLE_API_VERSION = "v3"

MAX_RESULTS = 50
PROCESSING_THREADS = 40

formatter = WebVTTFormatter()
q = queue.Queue()

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder")
args = parser.parse_args()
TRANSCRIPT_FOLDER = args.folder if args.folder else TRANSCRIPT_FOLDER


class Counter:
    '''thread safe counter'''

    def __init__(self):
        '''initialize the counter'''
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        '''increment the counter'''
        with self.lock:
            self.value += 1


counter = Counter()


def print_to_stderr(*a):
    '''print to stderr'''
    # Here a is the array holding the objects
    # passed as the argument of the function
    print(*a, file=sys.stderr)


def gen_metadata(playlist_item):
    '''Generate metadata for a video'''

    video_id = playlist_item['snippet']['resourceId']['videoId']
    filename = os.path.join(TRANSCRIPT_FOLDER, video_id + '.json')

    metadata = {}
    metadata['speaker'] = ''
    metadata['title'] = playlist_item['snippet']['title']
    metadata['videoId'] = playlist_item['snippet']['resourceId']['videoId']
    metadata['description'] = playlist_item['snippet']['description']

    # save the metadata as a .json file
    json.dump(metadata, open(filename, 'w', encoding='utf-8'))


def get_transcript(playlist_item, counter_id):
    '''Get the transcript for a video'''

    video_id = playlist_item['snippet']['resourceId']['videoId']
    filename = os.path.join(TRANSCRIPT_FOLDER, video_id + '.json.vtt')

    # if video transcript already exists, skip it
    if os.path.exists(filename):
        print_to_stderr(f"skipping video {counter_id}, {video_id}")
        return False

    try:

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # remove \n from the text
        for item in transcript:
            item['text'] = item['text'].replace('\n', ' ')

        print_to_stderr(
            f"Transcription download completed: {counter_id}, {video_id}")
        # save the transcript as a .vtt file
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(transcript, file, indent=4, ensure_ascii=False)
            # file.write(transcript)

    except Exception as e:
        print_to_stderr(e)
        print_to_stderr("Transcription not found for video: " + video_id)
        return False

    return True


def process_queue():
    '''process the queue'''
    while not q.empty():
        video = q.get()

        counter.increment()

        if get_transcript(video, counter.value):
            gen_metadata(video)

        q.task_done()


print_to_stderr(f"Transcription folder {TRANSCRIPT_FOLDER}")
print_to_stderr("Starting transcript download")

youtube = googleapiclient.discovery.build(
    GOOGLE_API_SERVICE_NAME, GOOGLE_API_VERSION, developerKey=GOOGLE_DEVELOPER_API_KEY)

# Create a request object with the playlist ID and the max results
request = youtube.playlistItems().list(
    part="snippet",
    playlistId=PLAYLIST_ID,
    maxResults=MAX_RESULTS
)

# Loop through the pages of results until there is no next page token
while request is not None:
    # Execute the request and get the response
    response = request.execute()

    # Iterate over the items in the response and append the video IDs to the list
    for item in response["items"]:
        q.put(item)

    # Get the next page token from the response and create a new request object
    next_page_token = response.get("nextPageToken")
    if next_page_token is not None:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=PLAYLIST_ID,
            maxResults=MAX_RESULTS,
            pageToken=next_page_token
        )
    else:
        request = None

print_to_stderr("Total transcriptions to be download: ", q.qsize())
start_time = time.time()

# create multiple threads to process the queue
threads = []
for i in range(PROCESSING_THREADS):
    t = threading.Thread(target=process_queue)
    t.start()
    threads.append(t)

# wait for all threads to finish
for t in threads:
    t.join()

finish_time = time.time()
print_to_stderr("Total time taken: ", finish_time - start_time)