#!/usr/bin/env python3
from subprocess import Popen, PIPE, call, check_call
import argparse, sys, os, requests
from pprint import pprint
import api.amara_api as amara
from utils import eprint, epprint

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
   parser.add_argument('--skip-errors', dest = 'skip', default = True, action = "store_true",
   help = '[default] Skip subtitles that could not be downloaded. \
         The list of failed YTIDs will be printed to \"failed_yt.dat\".')
   return parser.parse_args()

opts = read_cmd()
infile = opts.input_file
lang = opts.lang

# We suppose that the original language is English
original_video_lang = "en"
if lang == "en": 
    is_original = True # is lang the original language of the video?
else:
    is_original = False

print("# Syncing subtitles for language:", lang)

ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        ytids.append(line.split())

amara_api_key = amara.get_api_key()

# TODO: Move amara_headers into amara_api.py
# We really should create an amara class and have 
# amara_headers, api_key and session as private vars
amara_headers = {
   'Content-Type': 'application/json',
   'X-api-key': amara_api_key,
   'format': 'json'
}

call("rm -f youtubedl.err youtubedl.out", shell=True)

try:
    os.mkdir("subs")
except:
    pass

# Read file with existing videos to speed up the process
# Append every updated video
f_vids = open("videos_on_amara."+lang+".dat", "a+")
f_vids.seek(0)
ytid_exist = set()
for l in f_vids:
    ytid_exist.add(l.split()[0])

print("Current number of videos on Amara with subtitles in %s is: %d" % (lang, len(ytid_exist)))

# Skip certain videos
ytid_skip = set()
fname_skip = "sync_yt2amara_skip."+lang+".dat"
try:
    with open(fname_skip,"r") as f:
        for l in f:
            ytid_skip.add(l.split()[0])
    print("Current number of skipped videos on Amara:", len(ytid_skip))
except FileNotFoundError as e:
    pass

uploaded = 0
missing = 0

# create persistent session with Amara
am_ses = requests.Session()
f_failed_yt = "failed_download_yt.%s.dat" % (lang)


# Main loop
for i in range(len(ytids)):
    video_present = False
    lang_present  = False
    lang_visible  = False
    if len(ytids[i]) == 0 or ytids[i][0][0] == "#":
        print("")
        continue
    ytid = ytids[i][0]
    video_url = "https://www.youtube.com/watch?v=%s" % (ytid)

#   PART 1: Checking the existence of subtitles on Amara
    if ytid in ytid_skip:
        continue

    if ytid in ytid_exist and not opts.rewrite:
        continue

    sys.stdout.flush()
    sys.stderr.flush()
    f_vids.flush()

#   Check whether video is on Amara, if not create it
    amara_response = amara.check_video(video_url, amara_headers, s=am_ses)
    if not amara_response or amara_response['meta']['total_count'] == 0:
        video_present = False
        lang_present  = False
    else:
        video_present = True
        amara_id = amara_response['objects'][0]['id']
        amara_title = amara_response['objects'][0]['title']
        for lg in amara_response['objects'][0]['languages']:
            if lg["code"] == lang:
                lang_present = True
                # lang could be there, but with no revisions
                # this key was retired from API
                lang_visible = True
                #if lg["visible"] == True:
                #    lang_visible = True
                break
        lang_present, sub_version = amara.check_language(amara_id, lang, amara_headers, s  = am_ses)
        if lang_present and lang_visible and sub_version > 0:
            f_vids.write(ytid + '\n')
            if not opts.rewrite:
                print("Subtitles already on Amara for video YTID: ", ytid)    
                print("Use \"-r\" option to overwrite them")
                continue

    # Moved this here due to large number of Amara errors...
    if not video_present:
        amara_response = amara.add_video(video_url, original_video_lang, amara_headers, s=am_ses)
        if "id" in amara_response:
            amara_id = amara_response['id']
            amara_title =  amara_response['title']
        else:
            print("ERROR: During adding video to Amara:", ytid)
            continue
        if opts.verbose:
            print("Created video on Amara with Amara id "+amara_id)
            print(amara.AMARA_BASE_URL+'cs/videos/'+amara_id)


#   PART 2: GETTING THE SUBTITLES 
    yt_download_command = 'youtube-dl --sub-lang %s --sub-format %s --write-sub \
    --skip-download %s' % (lang, sub_format, video_url)
    
    p = Popen(yt_download_command, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    with open("youtubedl.out", "a") as f:
        f.write(out.decode('UTF-8'))
    if err:
        with open("youtubedl.err", "a") as f:
            f.write(err.decode('UTF-8'))
        if opts.verbose:
            print("WARNING during downloading subtitles for YTID=", ytid)
            print("Check file " + f_failed_yt)
        #continue

    fname = out.decode('UTF-8').split('Writing video subtitles to: ')
    if len(fname) < 2:
       print("ERROR: Requested subtitles were not found on YouTube. ", ytid)
       missing += 1
       with open(f_failed_yt,"a") as f:
           f.write(ytid+'\n')
       continue


    fname = fname[1].strip('\n')
    with open(fname, 'r') as content_file:
       subs = content_file.read()

    os.rename(fname,"subs/"+fname)

#   PART 3: Creating language on Amara

    if not lang_present:
        r = amara.add_language(amara_id, lang, is_original, amara_headers, s=am_ses)

#   PART 4: UPLOADING THE SUBTITLES 
    r = amara.upload_subs(amara_id, lang, is_complete, subs, sub_format, amara_headers, s=am_ses)
    if not 'version_number' in r:
        print("ERROR: Failed to upload subs to Amara for YTID=%s" % (ytid))
        epprint(r)
        continue
    else:
        print("Succesfully uploaded subtitles for YTID=%s AmaraID=%s" % (ytid, amara_id))
        uploaded += 1
        f_vids.write(ytid + '\n')


print("(: And we are finished! :)")
print("Succesfuly uploaded %d video subtitles." % (uploaded))
print("%d videos are missing subtitles on YT" % (missing))
