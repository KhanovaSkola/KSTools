#!/usr/bin/env python3
from subprocess import Popen, PIPE, call, check_call
import argparse, sys, os
from pprint import pprint
import api.amara_api as amara_api
import requests
from utils import answer_me


# We suppose that the uploaded subtitles are complete (non-critical)
is_complete = True # do we upload complete subtitles?
sub_format = 'srt'

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for downloading subtitles from Amara or YouTube. \
           The video from YouTube can be downloaded as well."
#  parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l','--lang',dest='lang',required = True, help='Which language do we download?')
   parser.add_argument('-y',dest='yt', action="store_true", help='Download subtitles from YouTube.')
   parser.add_argument('-a',dest='amara', action="store_true", help='Download subtitles from Amara.')
   parser.add_argument('-v','--video', dest='video', action="store_true", default=False, help='Download video from YouTube in addition to subtitles.')
   return parser.parse_args()

opts = read_cmd()
infile = opts.input_file
lang = opts.lang


if opts.yt == True and opts.amara == True:
    print('Conflicting options "-y" and "-a"')
    print('Type "-h" for help')
    sys.exit(1)
    
if opts.yt == False and opts.amara == False:
    print('Please, set either "-y" or "-a".')
    print('Type "-h" for help')
    sys.exit(1)

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        l = line.split()
        if l[0][0] != "#":
            ytids.append(line.split())

AMARA_API_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "SECRETS/amara_api_credentials.txt"))
# File 'apifile' should contain only one line with your Amara API key and Amara username.
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
if not opts.yt:
    file = open(AMARA_API_FILE, "r")
    API_KEY, USERNAME = file.read().split()[0:]
    print('Using Amara username: '+USERNAME)
    print('Using Amara API key: '+API_KEY)

call("rm -f youtubedl.out", shell=True)

amara_headers = {
   'Content-Type': 'application/json',
   'X-api-username': USERNAME,
   'X-api-key': API_KEY,
   'format': 'json'
}
# Create persistent HTTP session
# TODO: We should encapsulate Amara API in a class 
# and handle this internally!
ses = requests.Session()

# Main loop
for i in range(len(ytids)):
    ytid_from = ytids[i][0]

    video_url_from = 'https://www.youtube.com/watch?v='+ytid_from

#   GETTING THE SUBTITLES 
    if opts.yt:
        ytdownload = 'youtube-dl  --youtube-skip-dash-manifest  --sub-lang '+lang+ \
        ' --sub-format '+sub_format+' --write-sub '+ video_url_from
        if not opts.video:
            ytdownload = ytdownload + ' --skip-download'
            print(ytdownload)
    
        p = Popen(ytdownload, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        f = open("youtubedl.out", "a")
        f.write(out.decode('UTF-8'))
        f.close()
        if err:
            print(err)
            print("Error during downloading subtitles..")
            sys.exit(1)
        fname = out.decode('UTF-8').split('Writing video subtitles to: ')[1].strip('\n')
        print('Subtitles downloaded to file:'+fname)

    elif opts.amara == True:
        if opts.video:
            ytdownload = 'youtube-dl '+ video_url_from
            p = Popen(ytdownload, shell=True, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            f = open("youtubedl.out", "a")
            f.write(out.decode('UTF-8'))
            f.close()
            if err:
                print(err)
                print("Error during downloading video from YT.")
                sys.exit(1)
            else:
                print("Successfully downloaded the video.")

        # First, get first Amara ID
        amara_response = amara_api.check_video( video_url_from, amara_headers, s = ses)
        if amara_response['meta']['total_count'] == 0:
            print("ERROR: Source video is not on Amara! YT id"+ytid_from)
            sys.exit(1)
        else:
            amara_id_from =  amara_response['objects'][0]['id']
            amara_title =  amara_response['objects'][0]['title']
            print("Downloading "+lang+" subtitles from:")
            print("Title: "+amara_title)
            print(amara_api.AMARA_BASE_URL+'cs/videos/'+amara_id_from)

        # Check whether subtitles for a given language are present,
        is_present, sub_version = amara_api.check_language(amara_id_from, lang, amara_headers, s = ses)
        if is_present:
            print("Subtitle revision number: "+str(sub_version))
        else:
            print("ERROR: Amara does not have subtitles in "+lang+" language for this video!")
            sys.exit(1)
 
        # Download and write subtitles from Amara for a given language
        subs = amara_api.download_subs(amara_id_from, lang, sub_format, amara_headers, s = ses)
        f = open(ytid_from +'.'+lang+'.srt', "w")
        f.write(subs)
        f.close()


