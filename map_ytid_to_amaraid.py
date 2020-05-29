#!/usr/bin/env python3
import argparse, sys, requests
from pprint import pprint
from api.amara_api import Amara
from utils import answer_me

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for mapping YouTube IDs to Amara IDs. If given video is not on Amara, it is created."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l', '--lang', dest = 'lang', required = True, help='What language?')
   return parser.parse_args()

opts = read_cmd()
lang = opts.lang

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        ytids.append(line.split())

amara = Amara()

# Main loop
for i in range(len(ytids)):
    if len(ytids[i]) == 0:
        print("")
        continue
    ytid_from = ytids[i][0]

    sys.stdout.flush()
    sys.stderr.flush()

    video_url = 'https://www.youtube.com/watch?v=%s' % ytid_from

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url)
    if amara_response['meta']['total_count'] == 0:
        # Video is not yet on Amara so let's add it!
        amara_response = amara.add_video(video_url, lang)
        amara_id = amara_response['id']
        amara_title =  amara_response['title']
        sub_version = 0

    else:
        amara_id = amara_response['objects'][0]['id']
        amara_title = amara_response['objects'][0]['title']
        lang_present, sub_version = amara.check_language(amara_id, opts.lang)

    print("%s/%s/subtitles/editor/%s/%s/\t%s\t%s" % (amara.AMARA_BASE_URL, opts.lang, amara_id, opts.lang, sub_version, amara_title))

