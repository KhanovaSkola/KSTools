#!/usr/bin/python3
# Anaconda Python...for some reason does not work
##!/usr/bin/env python3
import os, sys, requests
from oauth2client.tools import argparser
import api.youtube_oauth as ytapi

# SAFETY MEASURE 
SUPPORTED_LANGUAGES = ['my']

# Download/upload subtitles in this format
SUB_FORMAT = 'vtt'

def read_cmd():
   """Read command line options."""
   parser = argparser
   parser.add_argument('input_file', metavar='INPUT_FILE', help='Text file containing YouTube IDs in the first column')
   parser.add_argument('-l','--lang', dest='lang', required = True, help='Subtitle language')
   parser.add_argument('-d','--dir', dest='dirname', required = True, help='Directory with subtitle files')
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

if not os.path.isdir(opts.dirname):
    print("Folder %s does not exist!" % opts.dirname)
    sys.exit(1)

# Create session with YT (I hope it is persistent)
youtube = ytapi.get_authenticated_service(opts)

uploaded = 0
# Main loop
for ytid in ytids:
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid
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

    subs_fname = "%s/%s.%s.%s" % (opts.dirname, ytid, opts.lang, SUB_FORMAT)

    # PART 3: UPLOAD SUBTITLES TO YOUTUBE
    if captions_present:
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
