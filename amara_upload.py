#!/usr/bin/env python
#from urllib2 import urlopen
from subprocess import Popen, PIPE, call, check_call
import requests, json
import argparse
from pprint import pprint
import sys

# File myAPI should contain only one line with your Amara API and Amara username
# Amara API can be found in Settins->Account-> API Access (bottom-right corner)
file = open("myAPI.txt", "r")
API_KEY, USERNAME = file.read().split()[0:]
print('Using Amara username: '+USERNAME)
print('Using Amara API key: '+API_KEY)

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
   'X-api-username': USERNAME,
   'X-api-key': API_KEY,
   'format': 'json'
}

# Amara functions should be independent of YouTube, pass video-url instead of ytid
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

def create_video(ytid, video_lang):
    url = amara_base_url + 'api/videos/'
    video_url = 'https://www.youtube.com/watch?v='+ytid
    body = { 
        'video_url': video_url,
        'primary_audio_language_code': video_lang
        }
    
    try:
        response = requests.post(url, data=json.dumps(body), headers=amara_headers )
        json_response = response.json()
    except requests.HTTPError as e:
        print e
        sys.exit(1)
    return json_response

def add_language(amara_id, lang, is_original):
    is_lang_present = False
    sub_version = 0
    url = amara_base_url+'/api/videos/'+amara_id+'/languages/'
    try:
        r = requests.get(url, headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print e
        sys.exit(1)

    #pprint(json_response)
    for obj in json_response['objects']:
        if obj['language_code'] == lang:
            is_lang_present = True
            sub_version = len(obj['versions'])
            break

    if json_response['meta']['total_count'] == 0 or not is_lang_present:
        url = amara_base_url + 'api/videos/'+amara_id+'/languages/'
        body = { 
            'language_code': lang,
            'subtitles_complete': False,  # To be uploaded later
            'is_primary_audio_language': is_original
            }
        try:
            response = requests.post(url, data=json.dumps(body), headers=amara_headers )
            json_response = response.json()
            pprint(json_response)
        except requests.HTTPError as e:
            print e
            sys.exit(1)

    return (is_lang_present, sub_version)


def upload_subs(amara_id, lang, is_complete, subs, sub_format):
    url = amara_base_url + 'api/videos/'+amara_id+'/languages/'+lang+'/subtitles/'
    body = { 
        'subtitles': subs,
        'sub_format': sub_format,
        'language_code': lang,
        'is_complete': is_complete,   # Warning, this is deprecated
        #'action': "Publish"
        'description': 'Subtitles copied from YouTube.'
        }
    try:
        response = requests.post(url, data=json.dumps(body), headers=amara_headers )
        #pprint(json_response)
        json_response = response.json()
    except requests.HTTPError as e:
        print e
        sys.exit(1)

    return json_response

def update_language():
    pass


"""
ytid='HIZV6Lhmi1M'
url = 'https://www.amara.org/api/videos/MqitMiqfXkBf/'
"""

lang = 'en'
is_original = True # is lang the original language of the video?
is_complete = True # do we upload complete subtitles?
sub_format = 'srt'

for ytid in ytids:
    ytdownload='youtube-dl --sub-lang "en" --sub-format "srt" --write-sub --skip-download '+ ytid
    
    p = Popen(ytdownload, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    f = open("youtubedl.out", "a")
    f.write(out)
    f.close()
    if err:
        print(err)
        print("Error during downloading subtitles..")
        sys.exit(1)
    fname = out.split('Writing video subtitles to: ')[1].strip('\n')
    print('Subtitles downloaded to file:'+fname)
    with open(fname, 'r') as content_file:
            subs = content_file.read()
    
    # Now check whether the video is already on Amara
    # If not, create it.
    amara_response = check_video_presence( ytid )
    if amara_response['meta']['total_count'] == 0:
        pprint(amara_response)
        print("Creating video on Amara with YTid "+ytid)
        amara_response = create_video(ytid, lang)
        amara_id = amara_response['id']
        amara_title =  amara_response['title']
        print("Created video on Amara with Amara id "+amara_id)
        print(amara_base_url+'cs/videos/'+amara_id)
    else:
        amara_id =  amara_response['objects'][0]['id']
        amara_title =  amara_response['objects'][0]['title']
        print("Video with YTid "+ytid+" is already present on Amara")
        print("Title: "+amara_title)
        print(amara_base_url+'cs/videos/'+amara_id)


    # First check, whether subtitles for a given language are present
    # then upload subtitles
    is_present, sub_version = add_language(amara_id, lang, is_original)
    if is_present and sub_version != 0:
        print("Language "+lang+" is already present in Amara video id:"+amara_id)
        print("Subtitle revision number: "+str(sub_version))
        print("Should I upload the subtitles anyway? [yes/no]")
        answer = ''
        while answer != "no" and answer != "yes":
            answer = raw_input('-->')
            if answer == "yes":
                r = upload_subs(amara_id, lang, is_complete, subs, sub_format)
                if r['version_no'] == sub_version+1:
                    print('Succesfully uploaded subtitles to: '+r['site_uri'])
            elif answer == "no":
                pass
            else:
                print("Please enter yes or no.")
    else:
        r = upload_subs(amara_id, lang, is_complete, subs, sub_format)
        print r['version_no']
        if r['version_no'] == sub_version+1:
            print('Succesfully uploaded subtitles to: '+r['site_uri'])
    print('----------------------------------------')


