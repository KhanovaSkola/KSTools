#!/usr/bin/env python
#from urllib2 import urlopen
from subprocess import Popen, PIPE, call, check_call
import requests
import urllib, urllib2, json
import argparse
from pprint import pprint
import sys

# File myAPI should contain only one line with your Amara API
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
file = open("myAPI.txt", "r")
API_KEY = file.read().rstrip('\n')
username = 'danekhollas' 

def read_cmd():
   """Function for reading command line options."""
#   usage = "usage: %prog [options] input_file"
   parser = argparse.ArgumentParser() #(Description="Read input parameters.")
   parser.add_argument('-i','--input',dest='input_file',required=True, help='List of YouTube IDs.')
   options = parser.parse_args(sys.argv[1:])
   inpfile = options.input_file
   return inpfile

ytids = []
input_file = read_cmd()

with open(input_file, "r") as f:
   for line in f:
       ytids.append(line.replace('\n', ''))

amara_base_url = 'https://www.amara.org/'
amara_headers = {
   'Content-Type': 'application/json',
   'X-api-username': username,
   'X-api-key': API_KEY,
   'format': 'json'
}

def add_language_en():
    pass

def check_video_presence(ytid):
    url = amara_base_url + 'api/videos/'
    video_url = 'https://www.youtube.com/watch?v='+ytid
    body = { 
        'video_url': video_url
        }
    try:
        response = requests.get(url, params=body, headers=amara_headers )
        json_response = response.json()
    except requests.HTTPError as e:
        print e
        sys.exit(1)

    return json_response

def create_video(amara_id, video_lang, video_url):
    pass

def add_language(amara_id, lang, srt):
    pass

def update_language():
    pass


"""
ytid='HIZV6Lhmi1M'
url = 'https://www.amara.org/api/videos/MqitMiqfXkBf/'
url='https://www.amara.org/api/videos/'
video_url = 'https://www.youtube.com/watch?v='+ytid
body = {'video_url': video_url}

amara_response = check_video_presence( ytid )
pprint(amara_response)
if len(amara_response['objects']) == 0:
    print("Creating video on Amara with YTID="+ytid)
    create_video()
else:
    amara_id =  amara_response['objects'][0]['id']
    print("Video is already present")
    print(amara_base_url+'/cs/videos/'+amara_id)

"""

for ytid in ytids:
    ytdownload='youtube-dl --sub-lang "en" --sub-format "srt" --write-sub --skip-download '+ ytid
    """
    p = Popen(ytdownload, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    print(out)
    if err:
        print(err)
        print("Error during downloading subtitles..")
        sys.exit(1)
    srtname=out.split()[-1]
    print srtname
    """
    # Now check whether video is already on Amara
    amara_response = check_video_presence( ytid )
    # TODO: we should really check for the presence of english language
    if len(amara_response['objects']) == 0:
        print("Creating video on Amara with YTID="+ytid)
#        create_video()
#        add_language()
        print('----------------------------------------')
    else:
        amara_id =  amara_response['objects'][0]['id']
        print("Video with YT id "+ytid+" is already present on Amara")
        print(amara_base_url+'/cs/videos/'+amara_id)
        print('----------------------------------------')


