#!/usr/bin/env python3
import argparse, sys
from pprint import pprint
from amara_api import *
from utils import answer_me

def read_cmd():
   """Function for reading command line options."""
   desc = "Program fro setting English as a primary language."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-c','--credentials',dest='apifile',default='myapi.txt', help='Text file containing your API key and username on the first line.')
   return parser.parse_args()

opts = read_cmd()
apifile = opts.apifile
video_lang = "en"

# File 'apifile' should contain only one line with your Amara API key and Amara username.
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
file = open(apifile, "r")
API_KEY, USERNAME = file.read().split()[0:]
print('Using Amara username: '+USERNAME)
#print('Using Amara API key: '+API_KEY)

amara_headers = {
   'Content-Type': 'application/json',
   'X-api-username': USERNAME,
   'X-api-key': API_KEY,
   'format': 'json'
}

infile = "videos_on_amara.en.dat"

ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        ytids.append(line.split())

#amara_id = ['iiAJyQ7lcTmE']
#for id in amara_id:
#    add_primary_audio_lang(id, video_lang, amara_headers)
#sys.exit(0)

# Skip certain videos
ytid_skip = set()
try:
    with open("skip_videos.dat","r") as f:
        for l in f:
            ytid_skip.add(l)
except:
    pass

# Main loop
for i in range(len(ytids)):
    ytid_from = ytids[i][0]
    sys.stdout.flush()
    sys.stderr.flush()

    video_url = 'https://www.youtube.com/watch?v='+ytid_from

#   Skip videos without en subtitles
    if ytid_from in ytid_skip:
        continue

    # Now check whether the video is already on Amara
    amara_response = check_video( video_url, amara_headers)
    lg = amara_response['objects'][0]['primary_audio_language_code'] 
    if amara_response['meta']['total_count'] == 0:
        print('ERROR: Video for this URL does not exist!', video_url)
        sys.exit(1)
    if lg != 'en' and lg != 'en-gb':
        amara_id =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print('Setting primary language for amara_id: ',amara_id)
        print('https://amara.org/videos/'+amara_id)
        r = add_primary_audio_lang(amara_id, video_lang, amara_headers)
        lg = r['primary_audio_language_code']
        if lg != video_lang:
            print("ERROR: Could not change primary audio language!")
            print('https://amara.org/videos/'+amara_id)
            sys.exit(1)

