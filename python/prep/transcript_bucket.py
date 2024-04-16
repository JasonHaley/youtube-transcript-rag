''' This script generates a master csv file from the transcript files.'''

from datetime import datetime, timedelta
import glob
import os
import json
import sys
import argparse

segments = []
TRANSCRIPT_FOLDER = os.getenv('TRANSCRIPT_FOLDER')

total_files = 0

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder")
args = parser.parse_args()

TRANSCRIPT_FOLDER = args.folder if args.folder else TRANSCRIPT_FOLDER


def print_to_stderr(*a):
    '''print to stderr'''
    # Here a is the array holding the objects
    # passed as the argument of the function
    print(*a, file=sys.stderr)


def gen_metadata_master(metadata):
    '''generate the metadata master csv file'''
    text = metadata['title'] + " " + metadata['description']

    text = text.strip()

    if text == "" or text is None:
        metadata['text'] = "No description available."
    else:
        # clean the text
        text = text.replace('\n', '')
        metadata['text'] = text.strip()

def clean_text(text):
    '''clean the text'''
    text = text.replace('\n', '') # remove new lines
    text = text.replace('&#39;', "'")
    text = text.replace('>>', '') # remove '>>'
    text = text.replace('  ', ' ') # remove double spaces

    return text

def parse_json_vtt_transcript(vtt, metadata):
    '''parse the json vtt file and return the transcript'''
    text = ""
    
    # add the speaker name to the transcript
    if 'speaker' in metadata and metadata['speaker'] != "":
        metadata['speaker'] = clean_text(metadata.get('speaker'))
        text = "The speaker's name is " + metadata['speaker'] + ". "

    # add the title to the transcript
    if 'title' in metadata and metadata['title'] != "":
        metadata['title'] = clean_text(metadata.get('title'))
        text += metadata.get('title') + ". "

    # add the description to the transcript
    if 'description' in metadata and metadata['description'] != "":
        metadata['description'] = clean_text(metadata.get('description'))
        text += metadata.get('description') + ". "

    # open the vtt file
    with open(vtt, 'r', encoding='utf-8') as json_file:
        json_vtt = json.load(json_file)

        for segment in json_vtt:        
            # add the text to the transcript
            text += clean_text(segment.get('text')) + " "
    
        metadata['text'] = text
        segments.append(metadata.copy())
        
def get_transcript(metadata):
    '''get the transcript from the .vtt file'''
    global total_files
    vtt = os.path.join(TRANSCRIPT_FOLDER, metadata['videoId'] + '.json.vtt')

    # check that the .vtt file exists
    if not os.path.exists(vtt):
        print_to_stderr("vtt file does not exist: ", vtt)
        return None
    else:
        print_to_stderr("Processing file: ", vtt)
        total_files += 1

    parse_json_vtt_transcript(vtt, metadata)


print_to_stderr(f"Transcription folder {TRANSCRIPT_FOLDER}")
folder = os.path.join(TRANSCRIPT_FOLDER, '*.json')

for file in glob.glob(folder):

    # load the json file
    meta = json.load(open(file, encoding='utf-8'))

    get_transcript(meta)


print_to_stderr("Total files: ", total_files)

# save segments to a json file
with open('./output/master.json', 'w', encoding='utf-8') as f:
    json.dump(segments, f, ensure_ascii=False, indent=4)
