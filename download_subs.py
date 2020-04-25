#!/usr/bin/env python3
import argparse, sys, os, requests
from subprocess import Popen, PIPE
from pprint import pprint
import api.amara_api as amara
from utils import answer_me, download_yt_subtitles

sub_format = 'srt'

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
   return parser.parse_args()

opts = read_cmd()

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
        l = line.split()
        if l[0][0] != "#":
            ytids.append(line.split())

if not os.path.isdir(opts.dirname):
    os.mkdir(opts.dirname)

try:
    os.remove("youtubedl.out")
    os.remove("youtubedl.err")
except:
    pass

if opts.amara:
    amara_api_key = amara.get_api_key()
    amara_headers = {
        'Content-Type': 'application/json',
        'X-api-key': amara_api_key,
        'format': 'json'
    }
    # Create persistent HTTP session
    # TODO: We should encapsulate Amara API in a class 
    # and handle this internally!
    ses = requests.Session()

# Main loop
for i in range(len(ytids)):

    ytid = ytids[i][0]
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid

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

        subs = download_yt_subtitles(opts.lang, sub_format, ytid, opts.dirname)

    elif opts.amara:

        # First, get Amara ID
        amara_response = amara.check_video(video_url, amara_headers, s = ses)
        if amara_response['meta']['total_count'] == 0:
            print("ERROR: Video is not on Amara! YTID=%s" % ytid)
            sys.exit(1)
        else:
            amara_id_from =  amara_response['objects'][0]['id']
            amara_title =  amara_response['objects'][0]['title']
            print("Downloading %s subtitles from:" % opts.lang)
            print("Title: %s" % amara_title)
            print(amara.AMARA_BASE_URL + 'cs/videos/' + amara_id_from)

        # Check whether subtitles for a given language are present,
        is_present, sub_version = amara.check_language(amara_id_from, opts.lang, amara_headers, s = ses)
        if is_present:
            print("Subtitle revision number: %d" % sub_version)
        else:
            print("ERROR: Amara does not have subtitles for language %s for this video!" % opts.lang)
            sys.exit(1)
 
        # Download and write subtitles from Amara for a given language
        subs = amara.download_subs(amara_id_from, opts.lang, sub_format, amara_headers, s = ses)
        fname = "%s/%s.%s.%s" % (opts.dirname, ytid, opts.lang, sub_format)
        with open(fname, 'w') as f:
            f.write(subs)

