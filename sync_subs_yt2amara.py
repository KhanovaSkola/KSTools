#!/usr/bin/env python3
from subprocess import Popen, PIPE, call, check_call
import argparse, sys, os, requests
from pprint import pprint
from api.amara_api import Amara
from utils import eprint, epprint, download_yt_subtitles

# We suppose that the uploaded subtitles are complete (non-critical)
is_complete = True # do we upload complete subtitles?

# DH TODO automatically handle missing YT sub formats
# converting to srt can be done via
# ffmpeg -i foo.vtt foo.srt
# currently youtube-dl convert does not work when not downloading the video
sub_format = 'vtt'
sub_format2 = "srt"

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for syncing subtitles from YouTube to Amara.\n \
           Optimized for larger number of subs, should be faster than script amara_upload.py."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE', help='Text file containing YouTube IDs in the first column.')
   parser.add_argument('-l','--lang', dest = 'lang', required = True, help='Which language do we copy?')
   parser.add_argument('-r','--rewrite', dest='rewrite', default = False, action = "store_true", help = 'Rewrite subs on Amara.')
   parser.add_argument('-v','--verbose', dest='verbose', default = False, action = "store_true", help = 'Verbose output.')
   parser.add_argument('--skip-errors', dest = 'skip', default = False, action = "store_true",
   help = 'Skip subtitles that could not be downloaded. \
         The list of failed YTIDs will be printed to \"failed_yt.dat\".')
   return parser.parse_args()

opts = read_cmd()

# We suppose that the original language is English
original_video_lang = "en"
if opts.lang == "en": 
    is_original = True # is lang the original language of the video?
else:
    is_original = False

print("# Syncing subtitles for language %s" % opts.lang)

ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        ytids.append(line.split())

try:
    os.remove("youtubedl.out")
    os.remove("youtubedl.err")
except:
    pass

TEMP_DIR = "subs"
try:
    os.mkdir(TEMP_DIR)
except:
    pass

# Read file with existing videos to speed up the process
# Append every updated video
f_vids = open("videos_on_amara.%s.dat" % opts.lang, 'a+')
f_vids.seek(0)
ytid_exist = set()
for l in f_vids:
    ytid_exist.add(l.split()[0])

print("Current number of videos on Amara with subtitles in %s is: %d" % (opts.lang, len(ytid_exist)))

# Skip certain videos
ytid_skip = set()
fname_skip = "sync_yt2amara_skip.%s.dat" % opts.lang
try:
    with open(fname_skip,"r") as f:
        for l in f:
            ytid_skip.add(l.split()[0])
    print("Current number of skipped videos on Amara:", len(ytid_skip))
except FileNotFoundError as e:
    pass

uploaded = 0
missing = 0

amara = Amara()

# Main loop
for i in range(len(ytids)):
    video_present = False
    lang_present  = False
    lang_visible  = False
    if len(ytids[i]) == 0 or ytids[i][0][0] == "#":
        print("")
        continue
    ytid = ytids[i][0]
    video_url = "https://www.youtube.com/watch?v=%s" % ytid

#   PART 1: Checking the existence of subtitles on Amara
    if ytid in ytid_skip:
        continue

    if ytid in ytid_exist and not opts.rewrite:
        continue

    sys.stdout.flush()
    sys.stderr.flush()
    f_vids.flush()

#   Check whether video is on Amara, if not create it
    amara_response = amara.check_video(video_url)
    if not amara_response or amara_response['meta']['total_count'] == 0:
        video_present = False
        lang_present  = False
    else:
        video_present = True
        amara_id = amara_response['objects'][0]['id']
        amara_title = amara_response['objects'][0]['title']
        for lg in amara_response['objects'][0]['languages']:
            if lg["code"] == opts.lang:
                lang_present = True
                # lang could be there, but with no revisions
                # this key was retired from API
                lang_visible = True
                #if lg["visible"] == True:
                #    lang_visible = True
                break
        lang_present, sub_version = amara.check_language(amara_id, opts.lang)
        if lang_present and lang_visible and sub_version > 0:
            f_vids.write(ytid + '\n')
            if not opts.rewrite:
                print("Subtitles already on Amara for video YTID=%s" % ytid)
                print("Use \"-r\" option to overwrite them")
                continue

    # Moved this here due to large number of Amara errors...
    if not video_present:
        amara_response = amara.add_video(video_url, original_video_lang)
        if "id" in amara_response:
            amara_id = amara_response['id']
            amara_title =  amara_response['title']
        else:
            print("ERROR: During adding video to Amara. YTID=%s" % ytid)
            continue
        if opts.verbose:
            print("Created video on Amara with AmaraId %s" % amara_id)
            print("%s/cs/videos/%s" % (amara.AMARA_BASE_URL, amara_id))


    # PART 2: GETTING THE SUBTITLES FROM YOUTUBE
    # imported from utils.py
    subs = download_yt_subtitles(opts.lang, sub_format, ytid, TEMP_DIR)

    # PART 3: Creating language on Amara
    if not lang_present:
        r = amara.add_language(amara_id, opts.lang, is_original)

    # PART 4: UPLOADING THE SUBTITLES
    r = amara.upload_subs(amara_id, opts.lang, is_complete, subs, sub_format)
    if not 'version_number' in r:
        print("ERROR: Failed to upload subs to Amara for YTID=%s" % ytid)
        epprint(r)
        continue
    else:
        print("Succesfully uploaded subtitles for YTID=%s AmaraID=%s" % (ytid, amara_id))
        uploaded += 1
        f_vids.write(ytid + '\n')


print("(: And we are finished! :)")
print("Succesfuly uploaded %d video subtitles." % uploaded)
print("%d videos are missing subtitles on YT" % missing)
