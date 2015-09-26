#!/usr/bin/env python3
from subprocess import Popen, PIPE, call, check_call
import argparse, sys
from pprint import pprint
from amara_api import *


# We suppose that the uploaded subtitles are complete (non-critical)
is_complete = True # do we upload complete subtitles?
sub_format = 'srt'

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for copying subtitles from YouTube to Amara."
   parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing a column of YouTube IDs.')
   parser.add_argument('-c','--credentials',dest='apifile',default='myapi.txt', help='Text file containing your API key and username on the first line.')
   parser.add_argument('-l','--lang',dest='lang',default='en', help='Which language should we copy?')
   return parser.parse_args()

opts = read_cmd()
infile = opts.input_file
apifile = opts.apifile
lang = opts.lang
# 

# We suppose that the original language is English
if lang == "en": 
    is_original = True # is lang the original language of the video?
else:
    is_original = False

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
       ytids.append(line.replace('\n', ''))

call("rm -f youtubedl.out", shell=True)

amara_headers = {
   'Content-Type': 'application/json',
   'X-api-username': USERNAME,
   'X-api-key': API_KEY,
   'format': 'json'
}


for ytid in ytids:
    video_url = 'https://www.youtube.com/watch?v='+ytid

    # Modify the following if you don't want to download subtitles
    ytdownload='youtube-dl  --youtube-skip-dash-manifest  --sub-lang '+lang+' --sub-format '+sub_format+' --write-sub --skip-download '+ video_url
    
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
    with open(fname, 'r') as content_file:
            subs = content_file.read()
    

    #### Here we already have subtitles to upload in variable subs

    # Now check whether the video is already on Amara
    # If not, create it.
    amara_response = check_video( video_url, amara_headers)
    if amara_response['meta']['total_count'] == 0:
        amara_response = add_video(video_url, lang, amara_headers)
        amara_id = amara_response['id']
        amara_title =  amara_response['title']
        print("Created video on Amara with Amara id "+amara_id)
        print("Title: "+amara_title)
        print(AMARA_BASE_URL+'cs/videos/'+amara_id)
    else:
        amara_id =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print("Video with YTid "+ytid+" is already present on Amara")
        print("Title: "+amara_title)
        print(AMARA_BASE_URL+'cs/videos/'+amara_id)


    # First check, whether subtitles for a given language are present,
    # then upload subtitles
    is_present, sub_version = check_language(amara_id, lang, amara_headers)
    if is_present:
        print("Language "+lang+" is already present in Amara video id:"+amara_id)
        print("Subtitle revision number: "+str(sub_version))
        answer = answer_me("Should I upload the subtitles anyway?")
        if not answer:
            break
    else:
        r = add_language(amara_id, lang, is_original, amara_headers)

    r = upload_subs(amara_id, lang, is_complete, subs, sub_format, amara_headers)
    if r['version_no'] == sub_version+1:
        print('Succesfully uploaded subtitles to: '+r['site_uri'])
    else:
        print("This is weird. Something probably went wrong during upload.")
        print("This is the response I got from Amara")
        pprint(r)
        sys.exit(1)

    print('----------------------------------------')



