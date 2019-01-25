#!/usr/bin/env python3
from __future__ import print_function
from subprocess import Popen, PIPE, call, check_call
import sys
from pprint import pprint
from amara_api import *
from utils import eprint, epprint
import os

import ytapi_captions_oauth as ytapi
from oauth2client.tools import argparser, run_flow


# We suppose that the uploaded subtitles are complete (non-critical)
is_complete = True # do we upload complete subtitles?

SAFE_MODE = True
#SUPPORTED_LANGUAGES = ['cs','bg','ko','pl']
SUPPORTED_LANGUAGES = ['cs']

sub_format = 'vtt'
sub_format2 = "srt"

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for syncing KA subtitles from Amara to YouTube.\n"
   parser = argparser
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs in the first column.')
   parser.add_argument('-d','--delimiter',dest='delim',default = None, help='Delimiter in text file')
   parser.add_argument('-l','--lang',dest='lang',default = "en", help='Which language do we copy?')
   parser.add_argument('-c',dest='amara_api_file', help='Text file containing your API key and username on the first line.')
#   parser.add_argument('-g',dest='google_api_file', help='Text file containing your Google credentials.')
   parser.add_argument('-u','--update',dest='update',default=False,action="store_true", help='Update captions even if present on YT.')
   parser.add_argument('-p','--publish', dest='publish', default=True, action="store_true", help='Publish subtitles.')
   parser.add_argument('-v','--verbose', dest='verbose', default=False, action="store_true", help='More verbose output.')
   return parser.parse_args()

opts = read_cmd()
infile = opts.input_file
amara_apifile = opts.amara_api_file

# TODO: use this somehow
#google_apifile = opts.google_api_file
lang = opts.lang
verbose = opts.verbose

if opts.publish:
    is_draft = False
else:
    is_draft = True

# We suppose that the original language is English
original_video_lang = "en"
if lang == "en": 
    is_original = True # is lang the original language of the video?
else:
    is_original = False


if lang not in SUPPORTED_LANGUAGES and SAFE_MODE:
    print("ERROR: We do not support upload for language "+lang)
    sys.exit(1)

print("# Syncing subtitles for language:", lang)
#answer = answer_me("# Is that okay?")
#if not answer:
#   sys.exit(1)

ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        l = line.split(opts.delim)
        if len(l) > 0 and l[0][0] != "#":
            ytids.append(l[0])
#with open(infile, "r") as f:
#    for line in f:
#        ytids.append(line.split(opts.delim)[0])

if len(ytids) < 20:
    print(ytids)

# File 'apifile' should contain only one line with your Amara API key and Amara username.
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
file = open(amara_apifile, "r")
API_KEY, USERNAME = file.read().split()[0:]
print('# Using Amara username: '+USERNAME)
#print('Using Amara API key: '+API_KEY)

amara_headers = {
   'Content-Type': 'application/json',
   'X-api-username': USERNAME,
   'X-api-key': API_KEY,
   'format': 'json'
}

temp_folder = 'subs'
try:
    os.mkdir(temp_folder)
except:
    pass

f_capts_yt = open("captions_on_yt."+lang+".dat", "a+")
f_capts_yt.seek(0)
# Using set instead of list for faster search
ytid_exist = set()
for l in f_capts_yt:
    ytid_exist.add(l.split()[0])

print("Current number of videos with subtitles on YT in "+lang+" is:", len(ytid_exist))

# Skip certain videos
# This file is user created
# you could e.g. copy file_missing to file_skip
fname_skip = "sync_amara2yt_skip."+lang+".dat"
ytid_skip = set()
try:
    with open(fname_skip,"r") as f:
        for l in f:
            ytid_skip.add(l.split()[0])
except FileNotFoundError as e:
    print('WARNING: Could not read file ',fname_skip)
except:
    print("Unexpected error:",  sys.exc_info()[0])
    raise

print("Current number of skipped videos on YouTube:", len(ytid_skip))

uploaded = 0


fname_missing = "amarasubs_missing."+lang+".dat"
fname_ytvid_missing = "ytvideo_missing.dat"
f_capts_missing = open(fname_missing, "a")
f_ytvid_missing = open(fname_ytvid_missing, "a")
missing = []

# create persistent session with Amara
am_ses = requests.Session()

# Create session with YT (should be persistent I hope)
youtube = ytapi.get_authenticated_service(opts)


# Main loop
for i in range(len(ytids)):
    video_present = False
    lang_present  = False
    lang_visible  = False
    amara_id = ''
    ytid_from = ytids[i]

    video_url_from = 'https://www.youtube.com/watch?v='+ytid_from
    video_url_to = 'https://www.youtube.com/watch?v='+ytid_from

#   PART 1: Checking the existence of subtitles on YouTube
    if (ytid_from in ytid_exist and not opts.update) or ytid_from in ytid_skip:
        continue

#    if verbose:
    print("Syncing YTID="+ytid_from)

    sys.stdout.flush()
    sys.stderr.flush()
    f_capts_yt.flush()
    f_capts_missing.flush()


    # For now, let's just crash if video is not on YT anymore
    # Helps to clean up the KS website
    try:
        captions = ytapi.list_captions(youtube, ytid_from, verbose=False)
    except:
        print("An exception occurred during listing of YTID = %s:\n" % ytid_from)
        print(sys.exc_info())
        f_ytvid_missing.write(ytid_from+'\n')
        continue

    captions_present = False
    for item in captions:
        id = item["id"]
        name = item["snippet"]["name"]
        language = item["snippet"]["language"]
        if language == lang:
            captions_present = True
            captionid = id

#   Check whether video is there
    amara_response = check_video(video_url_to, amara_headers, s=am_ses)
    if amara_response['meta']['total_count'] == 0:
        # I think this should virtually never happen?
        missing.append(ytid_from)
        f_capts_missing.write(ytid_from+'\n')
        print("Subtitles not found on Amara for YTID=", ytid_from)
        continue
    else:
        video_present = True
        amara_id = amara_response['objects'][0]['id']
        amara_title = amara_response['objects'][0]['title']
        # We don't really need check_language() here
        # This also avoids some API errors
        for lg in amara_response['objects'][0]['languages']:
            if lg["code"] == lang:
                lang_present = True
                # lang could be there, but with no revisions
                # this key was retired from API
                lang_visible = True
                #if lg["visible"] == True:
                #    lang_visible = True
                break
        lang_present, sub_version = check_language(amara_id, lang, amara_headers)
        if not lang_present or sub_version <= 0:
            missing.append(ytid_from)
            f_capts_missing.write(ytid_from+'\n')
            print("Subtitles not found on Amara for YTID=", ytid_from)
            continue

#   PART 2: GETTING THE SUBTITLES 
    subs = download_subs(amara_id, lang, sub_format, amara_headers, s=am_ses )
    subs_fname = temp_folder+'/'+ytid_from +'.'+lang+'.srt'
    with open(subs_fname, "w") as f:
        f.write(subs)


#   PART 3: UPLOADING THE SUBTITLES 

    if captions_present:
        if verbose:
            print("Subtitles already present for YTID=", ytid_from)
        f_capts_yt.write(ytid_from+'\n')
        if opts.update:
            print("Updating subtitles for YTID=", ytid_from)
            res = ytapi.update_caption(youtube, ytid_from, lang, captionid, is_draft, subs_fname);
            if res:
                uploaded +=1
    else:
        print("Uploading subtitles for YTID=", ytid_from)
        res = ytapi.upload_caption(youtube, ytid_from, lang, '', is_draft, subs_fname)
        if res:
            f_capts_yt.write(ytid_from+'\n')
            uploaded += 1


print("\n(:And we are finished!:)")
print(USERNAME+" have succesfuly uploaded ", uploaded, " videos.")

f_capts_yt.close()
f_capts_missing.close()
f_ytvid_missing.close()

if len(missing) != 0:
    print(len(missing)," videos are missing subtitles on Amara!")
    print("Those YTIDs are listed in file ", fname_missing)

