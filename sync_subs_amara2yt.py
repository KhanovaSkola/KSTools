#!/usr/bin/python3
# Anaconda Python...for some reason does not work
##!/usr/bin/env python3
import os, sys, requests
from oauth2client.tools import argparser

from utils import eprint, epprint
from api.amara_api import Amara
import api.youtube_oauth as ytapi

#SUPPORTED_LANGUAGES = ['cs','bg','ko','pl', 'my']
# SAFETY MEASURE 
SUPPORTED_LANGUAGES = ['cs']

# Download/upload subtitles in this format
SUB_FORMAT = 'vtt'

def read_cmd():
   """Read command line options."""
   parser = argparser
   parser.add_argument('input_file', metavar='INPUT_FILE', help='Text file containing YouTube IDs in the first column')
   parser.add_argument('-l','--lang', dest='lang', required = True, help='Subtitle language')
   parser.add_argument('-u','--update', dest='update', default=False, action="store_true", help='Update subtitles even if present on YT')
   parser.add_argument('-p','--publish', dest='publish', default=True, action="store_true", help='Publish subtitles')
   parser.add_argument('-v','--verbose', dest='verbose', default=False, action="store_true", help='Verbose output')
   return parser.parse_args()

opts = read_cmd()

if opts.publish:
    is_draft = False
else:
    is_draft = True

if opts.lang not in SUPPORTED_LANGUAGES:
    print("ERROR: We do not support upload for language " + opts.lang)
    print("If this is not a typo, modify variable \"SUPPORTED_LANGUAGES\"")
    sys.exit(1)

print("Syncing subtitles for language:", opts.lang)

ytids = []
# Reading file with YT id's
# We expect YT IDs in the first column
# We do not care about other columns
# We skip lines beginning with "#"
with open(opts.input_file, "r") as f:
    for line in f:
        l = line.split()
        if len(l) > 0 and l[0][0] != "#":
            ytids.append(l[0])


TEMP_FOLDER = 'subs'
if not os.path.isdir(TEMP_FOLDER):
    try:
        os.mkdir(TEMP_FOLDER)
    except:
        print("Could not create temp directory %s" % (TEMP_FOLDER))
        raise

amara = Amara()
youtube = ytapi.get_authenticated_service(opts)

uploaded = 0
# Main loop
for i in range(len(ytids)):
    video_present = False
    lang_present  = False
    lang_visible  = False
    amara_id = ''
    ytid = ytids[i]

    video_url = 'https://www.youtube.com/watch?v=%s' % ytid

    print("Syncing YTID %s" % ytid)

    sys.stdout.flush()
    sys.stderr.flush()

    captions = ytapi.list_captions(youtube, ytid, verbose = opts.verbose)

    captions_present = False
    for item in captions:
        id = item["id"]
        name = item["snippet"]["name"]
        language = item["snippet"]["language"]
        if language == opts.lang:
            captions_present = True
            captionid = id

    # PART 1: Check video on AMARA
    amara_response = amara.check_video(video_url)
    if amara_response['meta']['total_count'] == 0:
        print("Video not found on Amara for YTID %s" % ytid)
        sys.exit(1)
    else:
        video_present = True
        amara_id = amara_response['objects'][0]['id']
        amara_title = amara_response['objects'][0]['title']

        lang_present, sub_version = amara.check_language(amara_id, opts.lang)
        if not lang_present or sub_version <= 0:
            print("Subtitles not found on Amara for YTID=%s" % ytid)
            sys.exit(1)

    # PART 2: DOWNLOAD SUBTITLES FROM AMARA
    subs = amara.download_subs(amara_id, opts.lang, SUB_FORMAT)
    subs_fname = "%s/%s.%s.%s" % (TEMP_FOLDER, ytid, opts.lang, SUB_FORMAT)
    with open(subs_fname, "w", encoding="utf-8") as f:
        f.write(subs)

    # PART 3: UPLOAD SUBTITLES TO YOUTUBE
    if captions_present:
        if opts.verbose:
            print("Subtitles already present for YTID %s" % ytid)
        if opts.update:
            print("Updating subtitles for YTID %s " % ytid)
            res = ytapi.update_caption(youtube, ytid, opts.lang, captionid, is_draft, subs_fname);
            if res:
                uploaded +=1
            else:
                print("Unspecified ERROR while updating subtitles")
                sys.exit(1)
    else:
        print("Uploading new subtitles for YTID=", ytid)
        res = ytapi.upload_caption(youtube, ytid, opts.lang, '', is_draft, subs_fname)
        if res:
            uploaded += 1
        else:
            print("Unspecified ERROR while uploading subtitles")
            sys.exit(1)

print("\nFinished!")
print("Succesfuly uploaded %d videos." % uploaded)
