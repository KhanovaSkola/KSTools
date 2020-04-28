#!/usr/bin/env python3
import argparse, sys
from api.amara_api import Amara

def read_cmd():
   """Function for reading command line options."""
   desc = "Program fro setting English as a primary language on Amara videos."
   parser = argparse.ArgumentParser(description=desc)
   return parser.parse_args()

opts = read_cmd()
primary_video_lang = "en"

# TODO: This should be an input parameter!
infile = "videos_on_amara.en.dat"

ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        ytids.append(line.split())

amara = Amara()

# Main loop
for i in range(len(ytids)):
    ytid = ytids[i][0]
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid

    sys.stdout.flush()
    sys.stderr.flush()

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url)
    lg = amara_response['objects'][0]['primary_audio_language_code'] 
    if amara_response['meta']['total_count'] == 0:
        print('ERROR: Video for this URL does not exist!')
        print(video_url)
        sys.exit(1)
    if lg != 'en' and lg != 'en-gb':
        amara_id =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print('Setting primary language for amara_id: %s' % amara_id)
        print('%s/videos/%s' % (amara.AMARA_BASE_URL, amara_id))
        r = amara.add_primary_audio_lang(amara_id, primary_video_lang)
        lg = r['primary_audio_language_code']
        if lg != primary_video_lang:
            print("ERROR: Could not change primary audio language!")
            print('https://amara.org/videos/%s' % amara_id)
            sys.exit(1)

