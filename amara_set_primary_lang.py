#!/usr/bin/env python3
import argparse, sys
from pprint import pprint
import api.amara_api as amara
from utils import answer_me

def read_cmd():
   """Function for reading command line options."""
   desc = "Program fro setting English as a primary language on Amara videos."
   parser = argparse.ArgumentParser(description=desc)
   return parser.parse_args()

opts = read_cmd()
video_lang = "en"

amara_api_key = get_api_key()
amara_headers = {
   'Content-Type': 'application/json',
   'X-api-key': amara_api_key,
   'format': 'json'
}

# TODO: This should be an input parameter!
infile = "videos_on_amara.en.dat"

ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        ytids.append(line.split())

# Main loop
for i in range(len(ytids)):
    ytid = ytids[i][0]
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid

    sys.stdout.flush()
    sys.stderr.flush()

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url, amara_headers)
    lg = amara_response['objects'][0]['primary_audio_language_code'] 
    if amara_response['meta']['total_count'] == 0:
        print('ERROR: Video for this URL does not exist!')
        print(video_url)
        sys.exit(1)
    if lg != 'en' and lg != 'en-gb':
        amara_id =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print('Setting primary language for amara_id: %s' % amara_id)
        print('https://amara.org/videos/%s' % amara_id)
        r = amara.add_primary_audio_lang(amara_id, video_lang, amara_headers)
        lg = r['primary_audio_language_code']
        if lg != video_lang:
            print("ERROR: Could not change primary audio language!")
            print('https://amara.org/videos/%s' % amara_id)
            sys.exit(1)

