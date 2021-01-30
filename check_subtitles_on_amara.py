#!/usr/bin/env python3
import argparse, sys, requests
from time import sleep
from pprint import pprint

from api.amara_api import Amara

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for finding existing subtitles on Amara"
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE',
           help='Text file containing YouTube IDs.')
   parser.add_argument(
           '-s', '--sleep', dest = 'sleep_int',
           required = False, type = float, default = -1,
           help='Sleep interval (seconds)')
   parser.add_argument(
           '-l', '--lang', dest = 'lang',
           required = False, default = None,
           help='What language?')
   return parser.parse_args()

def find_subtitles(present_languages, lang, amara_id):
    """Check whether video on Amara has subtitles for a given lang
    present_langauges - part of response from amara.check_video
    lang - target language
    """
    subs_published = subs_incomplete = False
    for lang in present_languages:
        if lang['code'] == opts.lang:
            if lang['published']:
                subs_published = True
            else:
                is_present, sub_version = amara.check_language(amara_id, opts.lang)
                if is_present and sub_version > 0:
                    subs_incomplete = True
            break
    return subs_published, subs_incomplete

opts = read_cmd()
AMARA_TEAM = 'khan-academy'

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
    amara_team_id = amara_public_id = None

    # Check whether the video is already on Amara
    amara_response = amara.check_video(video_url)
    for r in amara_response['objects']:
        if r['team'] == AMARA_TEAM:
            amara_team_id = r['id']
            video_title = r['title']
            team_languages = r['languages']
        elif r['team'] is None:
            video_title = r['title']
            amara_public_id = r['id']
            public_languages = r['languages']


    if amara_team_id is not None:
        amara_url = "%s/%s/videos/%s/%s/?team=%s" % (
                amara.AMARA_BASE_URL,
                opts.lang,
                amara_team_id,
                opts.lang,
                AMARA_TEAM,
            )
        subs_published, subs_incomplete = find_subtitles(
                team_languages,
                opts.lang,
                amara_team_id
                )
        if subs_published:
            print("Subtitles published on Team Amara.\t%s\t%s\t%s\t%s\t%s" % (ytid, video_url,
                video_title, amara_team_id, amara_url))
        elif subs_incomplete:
            print("Incomplete subtitles found on Team Amara.\t%s\t%s\t%s\t%s\t%s" % (ytid, video_url,
                video_title, amara_team_id, amara_url))

    elif amara_public_id is not None:
        amara_url = "%s/%s/videos/%s/%s/" % \
                (amara.AMARA_BASE_URL, opts.lang, amara_public_id, opts.lang)
        subs_published, subs_incomplete = find_subtitles(
                public_languages,
                opts.lang,
                amara_public_id
                )
        if subs_published:
            print("Subtitles published on Public Amara.\t%s\t%s\t%s\t%s\t%s" % (ytid, video_url,
                video_title, amara_public_id, amara_url))
        elif subs_incomplete:
            print("Incomplete subtitles found on Public Amara.\t%s\t%s\t%s\t%s\t%s" % (ytid, video_url,
                video_title, amara_public_id, amara_url))
            print(lang)

