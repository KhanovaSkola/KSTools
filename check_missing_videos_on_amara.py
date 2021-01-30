#!/usr/bin/env python3
import argparse, sys, requests
from time import sleep

from api.amara_api import Amara

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for finding missing videos or subtitles on Team Amara"
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE',
           help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument(
           '-s', '--sleep', dest = 'sleep_int',
           required = False, type = float, default = -1,
           help='Sleep interval (seconds)')
   parser.add_argument(
           '-l', '--lang', dest = 'lang',
           required = False, default = None,
           help='What language?')
   return parser.parse_args()


opts = read_cmd()
amara_team = "khan-academy"

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        ytids.append(line.split())

AMARA_USERNAME = 'dhbot'
amara = Amara(AMARA_USERNAME)

# Main loop
for i in range(len(ytids)):
    if len(ytids[i]) == 0:
        print("")
        continue
    ytid = ytids[i][0]

    # Trying to reduce E 429
    if opts.sleep_int > 0:
        sleep(opts.sleep_int)

    sys.stdout.flush()
    sys.stderr.flush()

    video_url = 'https://www.youtube.com/watch?v=%s' % ytid
    amara_id = None

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url, amara_team)
    for r in amara_response['objects']:
        if r['team'] == amara_team:
            amara_id = r['id']

    if not amara_id:
        print("Video missing on %s Amara!\t%s" % (amara_team, video_url))
        continue

    # Optionally, we check for subtitles in a given language
    if opts.lang is not None:
        is_present, sub_version = amara.check_language(amara_id, opts.lang)
        if not is_present:
            print("%s subtitles missing\t%s" % (opts.lang, ytid))

