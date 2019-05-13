#!/usr/bin/env python3
import argparse, sys
from pprint import pprint
from amara_api import *
from utils import answer_me

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for mapping YouTube IDs to Amara IDs. If given video is not on Amara, it is created."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l','--lang',dest='lang',required = True, help='What language?')
   parser.add_argument('-c','--credentials',dest='apifile',default='myapi.txt', help='Text file containing your API key and username on the first line.')
   return parser.parse_args()

opts = read_cmd()
lang = opts.lang

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        ytids.append(line.split())

# File 'apifile' should contain only one line with your Amara API key and Amara username.
# Amara API can be found in Settings -> Account -> API Access (bottom-right corner)
file = open(opts.apifile, "r")
API_KEY, USERNAME = file.read().split()[0:]

amara_headers = {
   'Content-Type': 'application/json',
   'X-api-username': USERNAME,
   'X-api-key': API_KEY,
   'format': 'json'
}

# Create persistent HTTP session
ses = requests.Session()

# Main loop
for i in range(len(ytids)):
    if len(ytids[i]) == 0:
        print("")
        continue
    ytid_from = ytids[i][0]

    sys.stdout.flush()
    sys.stderr.flush()

    video_url = 'https://www.youtube.com/watch?v='+ytid_from

    # Check whether the video is already on Amara
    amara_response = check_video( video_url, amara_headers, s = ses)
    if amara_response['meta']['total_count'] == 0:
        #amara_response = add_video(video_url, lang, amara_headers)
        #amara_id = amara_response['id']
        #amara_title =  amara_response['title']
        #print(ytid_from, AMARA_BASE_URL+'cs/subtitles/editor/'+amara_id+'/'+lang)
        print("Video not on Amara!", ytid_from)
    else:
        amara_id = amara_response['objects'][0]['id']
        amara_title = amara_response['objects'][0]['title']
        lang_present, sub_version = check_language(amara_id, opts.lang, amara_headers, s = ses)
        print(AMARA_BASE_URL + opts.lang + '/subtitles/editor/' + amara_id + '/' + opts.lang, '\t', sub_version, '\t', amara_title)

