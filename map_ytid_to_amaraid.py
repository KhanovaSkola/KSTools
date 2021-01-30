#!/usr/bin/env python3
import argparse, sys, requests
from pprint import pprint
from api.amara_api import Amara
from utils import answer_me

def print_header():
    print("Amara link | Number of subtitle revisions | Video Title")

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for mapping YouTube IDs to Amara IDs. If given video is not on Amara, it is created."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l', '--lang', dest = 'lang',
          required = True, help='What language?')
   parser.add_argument('--amara-public', dest = 'amara_public',
          action = 'store_true', 
          help='Generate links to Amara public workspace.')
   parser.add_argument('--no-header', dest = 'header',
          action = 'store_false', default = True,
          help='Print header.')
   return parser.parse_args()


opts = read_cmd()
lang = opts.lang
amara_team = "khan-academy"
if opts.amara_public:
    amara_team = None

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        ytids.append(line.split())

AMARA_USERNAME = 'dhbot'
amara = Amara(AMARA_USERNAME)

if opts.header:
    print_header()

# Main loop
for i in range(len(ytids)):
    if len(ytids[i]) == 0:
        print("")
        continue
    ytid = ytids[i][0]

    sys.stdout.flush()
    sys.stderr.flush()

    video_url = 'https://www.youtube.com/watch?v=%s' % ytid

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url, amara_team)
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

    if amara_team:
        amara_link = "%s/%s/videos/%s/%s/?team=%s" % \
                (amara.AMARA_BASE_URL, opts.lang, amara_id, opts.lang, amara_team)
    else:
        amara_link = "%s/%s/subtitles/editor/%s/%s/" % (amara.AMARA_BASE_URL,
            opts.lang, amara_id, opts.lang)


    print("%s\t%s\t%s" % (amara_link, sub_version, amara_title))
    #title = amara_title.split("|")[0].strip().lower().replace(' ','_')
    #print("%s\t%s" % (ytid, title))

