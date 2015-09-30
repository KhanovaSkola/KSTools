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
   desc = "Program for uploading subtitles to Amara. There are three modes of operation, depending on the source of the subtitles. \
           You can get the subtitles from YouTube, or upload subtitles files, or copy subtitles between Amara videos. \
           The format of the input file depends on the mode of operation."
#  parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l','--lang',dest='lang',required = True, help='Which language do we copy?')
   parser.add_argument('-f',dest='files', action="store_true",  help='Upload subtitles from files to Amara.')
   parser.add_argument('-y',dest='yt', action="store_true", help='Download subtitles from YouTube and upload them to Amara.')
   parser.add_argument('-a',dest='amara', action="store_true", help='Copy subtitles between two same Amara videos.')
   parser.add_argument('-c','--credentials',dest='apifile',default='myapi.txt', help='Text file containing your API key and username on the first line.')
   return parser.parse_args()

opts = read_cmd()
infile = opts.input_file
apifile = opts.apifile
lang = opts.lang

# We suppose that the original language is English
if lang == "en": 
    is_original = True # is lang the original language of the video?
else:
    is_original = False

if opts.yt == True and opts.files == True and opts.amara == True:
    print('Conflicting options "-f", "-y" and/or "-a"')
    print('Type "-h" for help')
    sys.exit(1)
    
if opts.yt == False and opts.files == False and opts.amara == False:
    print('Please, set either "-f", "-y" or "-a".')
    print('Type "-h" for help')
    sys.exit(1)

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        ytids.append(line.split())

# File 'apifile' should contain only one line with your Amara API key and Amara username.
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
file = open(apifile, "r")
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

print("This is what I got from the input file:")
print(ytids)

answer = answer_me("Should I proceed?")
if not answer:
    sys.exit(1)


# Main loop
for i in range(len(ytids)):
    ytid_from = ytids[i][0]

    if opts.amara == True:
        ytid_to = ytids[i][1]
    else:
        ytid_to = ytids[i][0]

    video_url_from = 'https://www.youtube.com/watch?v='+ytid_from
    video_url_to = 'https://www.youtube.com/watch?v='+ytid_to

#   PART 1: GETTING THE SUBTITLES 
    if opts.yt == True:
        ytdownload = 'youtube-dl  --youtube-skip-dash-manifest  --sub-lang '+lang+ \
        ' --sub-format '+sub_format+' --write-sub --skip-download '+ video_url_from
    
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

    elif opts.files == True:
        f = open(ytids[i][1],"r")
        subs = f.read()

    elif opts.amara == True:
        # First, get first Amara ID
        amara_response = check_video( video_url_from, amara_headers)
        if amara_response['meta']['total_count'] == 0:
            print("ERROR: Source video is not on Amara! YT id"+ytid_from)
            sys.exit(1)
        else:
            amara_id_from =  amara_response['objects'][0]['id']
            amara_title =  amara_response['objects'][0]['title']
            print("Copying "+lang+" subtitles from:")
            print("Title: "+amara_title)
            print(AMARA_BASE_URL+'cs/videos/'+amara_id_from)

        # Check whether subtitles for a given language are present,
        is_present, sub_version = check_language(amara_id_from, lang, amara_headers)
        if is_present:
            print("Subtitle revision number: "+str(sub_version))
        else:
            print("ERROR: Amara does not have subtitles in "+lang+" language for this video!")
            sys.exit(1)
 
        # Download subtitles from Amara for a given language
        subs = download_subs(amara_id_from, lang, sub_format, amara_headers )


#   PART 2: UPLOADING THE SUBTITLES 

    # Now check whether the video is already on Amara
    # If not, create it.
    amara_response = check_video( video_url_to, amara_headers)
    if amara_response['meta']['total_count'] == 0:
        amara_response = add_video(video_url_to, lang, amara_headers)
        amara_id = amara_response['id']
        amara_title =  amara_response['title']
        print("Created video on Amara with Amara id "+amara_id)
        print("Title: "+amara_title)
        print(AMARA_BASE_URL+'cs/videos/'+amara_id)
    else:
        amara_id =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print("Video with YTid "+ytid_to+" is already present on Amara")
        print("Title: "+amara_title)
        print(AMARA_BASE_URL+'cs/videos/'+amara_id)

    # When copying between 2 Amara videos, make sure that they have the same length
    # If not, ask the user whether to proceed anyway (might screw up the subs timing)
    if opts.amara == True:
        compare_videos(amara_id_from, amara_id, amara_headers)

    # First check, whether subtitles for a given language are present,
    # then upload subtitles
    is_present, sub_version = check_language(amara_id, lang, amara_headers)
    if is_present:
        print("Language "+lang+" is already present in Amara video id:"+amara_id)
        print("Subtitle revision number: "+str(sub_version))
        answer = answer_me("Should I upload the subtitles anyway?")
        if not answer:
            continue
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



