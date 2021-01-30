#!/usr/bin/env python3
import argparse, sys, os, requests
from subprocess import Popen, PIPE
from pprint import pprint
from api.amara_api import Amara
from utils import answer_me, download_yt_subtitles
from time import sleep

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for downloading subtitles from Amara or YouTube. \
           The video from YouTube can be downloaded as well."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l','--lang', dest='lang', required = True, help='Which language do we download?')
   parser.add_argument('-y', dest='youtube', action="store_true", help='Download subtitles from YouTube.')
   parser.add_argument('-a', dest='amara', action="store_true", help='Download subtitles from Amara.')
   parser.add_argument('-v', '--video', dest='video', action="store_true", default=False, help='Download video from YouTube in addition to subtitles.')
   parser.add_argument('-d', '--dir', dest='dirname', default='subs', help='Destination directory for subtitles')
   parser.add_argument(
           '--sub-format', dest = 'sub_format',
           required = False, default = 'vtt',
           help='What language?')
   parser.add_argument(
           '-s', '--sleep', dest = 'sleep_int',
           required = False, type = float, default = -1,
           help='Sleep interval (seconds)')
   return parser.parse_args()

opts = read_cmd()
if opts.youtube and opts.sub_format != 'vtt':
    eprint("ERROR: YouTube download only support vtt format!")
    sys.exit(1)

if opts.youtube == True and opts.amara == True:
    print('Conflicting options "-y" and "-a"')
    print('Type "-h" for help')
    sys.exit(1)
    
if opts.youtube == False and opts.amara == False:
    print('Please, set either "-y" or "-a".')
    print('Type "-h" for help')
    sys.exit(1)

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        l = line.split(' ')
        if l[0][0] != "#":
            ytids.append(line.split())

if not os.path.isdir(opts.dirname):
    os.mkdir(opts.dirname)

try:
    os.remove("youtubedl.out")
    os.remove("youtubedl.err")
except:
    pass

AMARA_USERNAME = 'dhbot'
if opts.amara:
    amara = Amara(AMARA_USERNAME)

# Main loop
for i in range(len(ytids)):

    ytid = ytids[i][0]
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid
    amara_id = ''

    if opts.video:
        video_download_cmd = "youtube-dl %s" % video_url
        p = Popen(video_download_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        with open("youtubedl.out", 'a') as f:
            f.write(out.decode('UTF-8'))
        if err:
            print(err)
            sys.exit(1)
        else:
            print("Successfully downloaded video from %s" % video_url)

    if opts.youtube:

        subs = download_yt_subtitles(opts.lang, opts.sub_format, ytid, opts.dirname)

    elif opts.amara:

        # TODO: Extract this to utils as well.

        # First, get Amara ID
        amara_response = amara.check_video(video_url)
        if amara_response['meta']['total_count'] == 0:
            print("ERROR: Video is not on Amara! YTID=%s" % ytid)
            sys.exit(1)
        else:
            amara_id =  amara_response['objects'][0]['id']
            amara_title =  amara_response['objects'][0]['title']
            print("Downloading %s subtitles for YTID=%s" % (opts.lang, ytid))
            print("Title: %s" % amara_title)
            print("%s/cs/videos/%s" % (amara.AMARA_BASE_URL, amara_id))

        # Check whether subtitles for a given language are present,
        is_present, sub_version = amara.check_language(amara_id, opts.lang)
        if is_present and sub_version > 0:
            print("Subtitle revision number: %d" % sub_version)
        else:
            print("ERROR: Amara does not have subtitles for language %s for this video!" % opts.lang)
            sys.exit(1)
 
        # Download and write subtitles from Amara for a given language
        subs = amara.download_subs(amara_id, opts.lang, opts.sub_format)
        fname = "%s/%s.%s.%s" % (opts.dirname, ytid, opts.lang, opts.sub_format)
        with open(fname, 'w') as f:
            f.write(subs)

    # Trying to reduce E 429
    if opts.sleep_int > 0:
        sleep(opts.sleep_int)

