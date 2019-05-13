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
infile = opts.input_file
apifile = opts.apifile
lang = opts.lang

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        ytids.append(line.split())

# File 'apifile' should contain only one line with your Amara API key and Amara username.
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
file = open(apifile, "r")
API_KEY, USERNAME = file.read().split()[0:]
#print('Using Amara username: '+USERNAME)
#print('Using Amara API key: '+API_KEY)

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
    title = ''
    if len(ytids[i]) > 2:
        for t in ytids[i][1:]:
            title = title + ' ' + t

    sys.stdout.flush()
    sys.stderr.flush()

    video_url = 'https://www.youtube.com/watch?v='+ytid_from

    # Now check whether the video is already on Amara
    # If not, create it.
    amara_response = check_video( video_url, amara_headers, s = ses)
    if amara_response['meta']['total_count'] == 0:
        #amara_response = add_video(video_url, lang, amara_headers)
        #amara_id = amara_response['id']
        #amara_title =  amara_response['title']
        #print(ytid_from, AMARA_BASE_URL+'cs/subtitles/editor/'+amara_id+'/'+lang)
        print("Video not on Amara!",ytid_from)
    else:
        amara_id = amara_response['objects'][0]['id']
        amara_title = amara_response['objects'][0]['title']
#        print(amara_response['objects'])
        #print(amara_id,'\t',AMARA_BASE_URL+lang+'/subtitles/editor/'+amara_id+'/'+lang,'\t',title)
        print(AMARA_BASE_URL+lang+'/subtitles/editor/'+amara_id+'/'+lang,'\t',title)

