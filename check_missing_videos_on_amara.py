#!/usr/bin/env python3
import argparse, sys, requests
from time import sleep

from api.amara_api import Amara

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for mapping YouTube IDs to Amara IDs. If given video is not on Amara, it is created."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE',
           help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument(
           '-s', '--sleep', dest = 'sleep_int',
           required = False, type = float, default = -1,
           help='Sleep interval (seconds)')
   return parser.parse_args()


opts = read_cmd()
amara_team = "khan-academy"

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
    ytid = ytids[i][0]

    # Trying to reduce E 429
    if opts.sleep_int > 0:
        sleep(opts.sleep_int)

    sys.stdout.flush()
    sys.stderr.flush()

    video_url = 'https://www.youtube.com/watch?v=%s' % ytid

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url, amara_team)
    if amara_response['meta']['total_count'] == 0:
        # We're printing videos that are missing on Team Amara
        print(video_url)

