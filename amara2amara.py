#!/usr/bin/env python3
from subprocess import Popen, PIPE, call, check_call
import argparse, sys
from pprint import pprint
from amara_api import *


# TODO: check the length of both videos to ensure that we are copying between the same videous

# We suppose that the uploaded subtitles are complete (non-critical)
is_complete = True
# This should only be changed, if we support lang="all" option
# Which is probably not a good idea anyway

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for copying subtitles from YouTube to Amara."
   parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing two columns of YouTube IDs.')
   parser.add_argument('-c','--credentials',dest='apifile',default='myapi.txt', help='Text file containing your API key and username on the first line.')
   parser.add_argument('-l','--lang',dest='lang',default='en', help='Which language should we copy (can be "all" for all of them)?')
   return parser.parse_args()

opts = read_cmd()
infile = opts.input_file
apifile = opts.apifile
lang = opts.lang
# 

# File 'apifile' should contain only one line with your Amara API key and Amara username.
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
file = open(apifile, "r")
API_KEY, USERNAME = file.read().split()[0:]
print('Using Amara username: '+USERNAME)
print('Using Amara API key: '+API_KEY)

# Reading file with YT id's
ytids = []
with open(infile, "r") as f:
   for line in f:
       ytids.append(line.split())

amara_headers = {
   'Content-Type': 'application/json',
   'X-api-username': USERNAME,
   'X-api-key': API_KEY,
   'format': 'json'
}


for ytid in ytids:
    video_url_from = 'https://www.youtube.com/watch?v='+ytid[0]
    video_url_to = 'https://www.youtube.com/watch?v='+ytid[1]
    sub_format = 'srt'

    # First, get first Amara ID
    amara_response = check_video( video_url_from, amara_headers)
    if amara_response['meta']['total_count'] == 0:
        print("ERROR: Source video is not on Amara! YT id"+utid_id[0])
        sys.exit(1)
    else:
        amara_id_from =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print("Copying "+lang+" subtitles from:")
        print("Title: "+amara_title)
        print(AMARA_BASE_URL+'cs/videos/'+amara_id_from)

    # First check, whether subtitles for a given language are present,
    is_present, sub_version = check_language(amara_id_from, lang, amara_headers)
    if is_present:
        print("Subtitle revision number: "+str(sub_version))
    else:
        print("ERROR: Amara does not have subtitles in "+lang+" language for this video!")
        sys.exit(1)

    # Download subtitles from Amara for a given language
    subs = download_subs(amara_id_from, lang, sub_format, amara_headers )


    # Now check whether the second video is already on Amara
    # If not, create it.
    amara_response = check_video( video_url_to, amara_headers)
    if amara_response['meta']['total_count'] == 0:
        amara_response = add_video(video_url, lang, amara_headers)
        amara_id_to = amara_response['id']
        amara_title =  amara_response['title']
        print("Created video on Amara with Amara id "+amara_id_to)
        print("Title: "+amara_title)
        print(AMARA_BASE_URL+'cs/videos/'+amara_id_to)
    else:
        amara_id_to =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print("Copying to: ")
        print("Title: "+amara_title)
        print(AMARA_BASE_URL+'cs/videos/'+amara_id_to)


    # First check, whether subtitles for a given language are present,
    # then upload subtitles
    is_present, sub_version = check_language(amara_id_to, lang, amara_headers)
    if is_present:
        print("Language "+lang+" is already present in Amara video id:"+amara_id_to)
        print("Subtitle revision number: "+str(sub_version))
        answer = answer_me("Should I rewrite it?")
        if not answer:
            print('----------------------------------------')
            break

    else:
        r = add_language(amara_id_to, lang, is_original, amara_headers)

    r = upload_subs(amara_id_to, lang, is_complete, subs, sub_format, amara_headers)
    pprint(r)
    if r['version_no'] == sub_version+1:
        print('Succesfully uploaded subtitles to: '+r['site_uri'])
    else:
        print("This is weird. Something probably went wrong during upload.")
        print("This is the response I got from Amara")
        pprint(r)
        sys.exit(1)

    print('----------------------------------------')

