#!/usr/bin/env python3
import argparse, sys, requests
from time import sleep
from pprint import pprint
from api.amara_api import Amara
from utils import answer_me

def read_cmd():
   desc = "Deleting Subtitle Requests on Amara in bulk"
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs.')
   parser.add_argument(
           '-l', '--lang', dest = 'lang',
           required = True,
           help='Language code')
   parser.add_argument(
           '-s', '--sleep', dest = 'sleep_int',
           required = False, type = float, default = -1,
           help='Sleep interval (seconds)')
   return parser.parse_args()


opts = read_cmd()
lang = opts.lang
AMARA_USERNAME = 'danekhollas'
AMARA_TEAM = "khan-academy"

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        ytids.append(line.split())

amara = Amara(AMARA_USERNAME)

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
    amara_response = amara.check_video(video_url, AMARA_TEAM)
    if amara_response['meta']['total_count'] == 0:
        # Video is not yet on Amara so let's add it!
        print("ERROR: Video not found on Amara!")
        sys.exit(1)

    amara_id = amara_response['objects'][0]['id']
    amara_title = amara_response['objects'][0]['title']

    # Trying to reduce E 429
    if opts.sleep_int > 0:
        sleep(opts.sleep_int)

    subs_request = amara.list_subtitle_requests(amara_id, opts.lang, AMARA_TEAM)
    if subs_request['meta']['total_count'] == 0:
        print("Subtitle request not found, skipping...YTID\t%s" % ytid)
        continue

    job_id = subs_request['objects'][0]['job_id']
    work_status = subs_request['objects'][0]['work_status']
    if work_status != 'needs-subtitler':
        print("Subtitle request is being worked on. YTID:\t%s" % ytid)
        continue

    http_status = amara.delete_subtitle_request(job_id, AMARA_TEAM)
    if http_status != 204:
        print("ERROR when deleting the subtitle request YTID=%s. HTTP code: %d"
                % (ytid, http_status))

    print("Subtitle request successfuly deleted. YTID\t%s" % ytid)
