#!/usr/bin/env python3
import argparse, sys, requests
from pprint import pprint
from api.amara_api import Amara
from utils import answer_me

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for syncing subtitles from public Amara to Khan Academy Team Amara."
   parser = argparse.ArgumentParser(description=desc)
   # TODO: Add option to mark subs as complete
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l', '--lang', dest = 'lang', required = True, help='What language?')
   return parser.parse_args()

opts = read_cmd()
lang = opts.lang

AMARA_TEAM = "khan-academy"
AMARA_USERNAME = 'danekhollas'
SUB_FORMAT = 'vtt'

# TODO: Figure out whether this is something we should be getting from the 
# public Amara API?
IS_COMPLETE = True

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

    # 1. DOWNLOAD SUBS FROM PUBLIC AMARA

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url)
    if amara_response['meta']['total_count'] == 0:
        eprint("ERROR: Source video is not on Amara! YTID=%s" % ytid)
        sys.exit(1)

    amara_id_public = amara_response['objects'][0]['id']
    amara_title = amara_response['objects'][0]['title']
    # print("Copying %s subtitles for YTID ", lang, ytid)
    print("Title: %s" % amara_title)

    # Check whether subtitles for a given language are present,
    is_present, sub_version_public = amara.check_language(amara_id_public, lang)
    if is_present:
        print("Subtitle revision %d (Public Amara)" % sub_version_public)
    else:
        print("ERROR: Amara does not have subtitles in %s language for this \
                video!" % lang)
        sys.exit(1)
 
    # Download subtitles from Amara for a given language
    subs = amara.download_subs(amara_id_public, lang, SUB_FORMAT)

    # 2. UPLOAD TO PRIVATE KHAN ACADEMY AMARA
    # Check whether the video is already on Amara
    amara_id_private = None
    amara_response = amara.check_video(video_url, AMARA_TEAM)
    for r in amara_response['objects']:
        if r['team'] == AMARA_TEAM:
            amara_id_private = r['id']

    if not amara_id_private:
        eprint("ERROR: Video is not on Khan Academy Amara! YTID=%s" % ytid)
        sys.exit(1)

    # Check whether video has complete subtitles on Amara Team or not
    r = amara.list_subtitle_requests(amara_id_private, opts.lang, AMARA_TEAM)
    if r['meta']['total_count'] != 0:
        job_id = r['objects'][0]['job_id']
        r = amara.assign_video(job_id, amara_team)
        # TODO: Check status
        pprint(r)

    is_present, sub_version_private = amara.check_language(amara_id_private, opts.lang)
    if is_present:
        print("Subtitle revision %d (Public Amara)" % sub_version_private)

    #print(amara.list_actions(amara_id_private, opts.lang))
    r = amara.upload_subs(amara_id_private, lang, IS_COMPLETE, subs, SUB_FORMAT)
    sub_version_new = r['version_number']
    if sub_version_new != sub_version_private + 1:
        eprint("ERROR: Something went wrong during subtitle upload")
        eprint(r)
        sys.exit(1)

    # 3. TODO: Mark video as published



