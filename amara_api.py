#!/usr/bin/env python3
import json, sys
import requests 
from pprint import pprint
from utils import *

AMARA_BASE_URL = 'https://www.amara.org/'
EXIT_ON_HTTPERROR  = False


def check_video(video_url, amara_headers):
    url = AMARA_BASE_URL + 'api/videos/'
    body = { 
        'video_url': video_url
        }
    try:
        r = requests.get(url, params=body, headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        eprint('Error for video',video_url)
        eprint(e,"in amara_api::check_video")
        try:
            eprint(r.json())
        except:
            # Catch exceprtion when r.json is empty
            pass
        sys.exit(1)

    return json_response


def add_video(video_url, video_lang, amara_headers):
    url = AMARA_BASE_URL + 'api/videos/'
    body = { 
        'video_url': video_url,
        'primary_audio_language_code': video_lang
        }
    
    try:
        r = requests.post(url, data=json.dumps(body), headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        eprint('ERROR for video',video_url)
        eprint(e,"in amara_api::add_video")
        try:
            eprint(r.json())
        except:
            # Catch exceprtion when r.json is empty
            pass
        if EXIT_ON_HTTPERROR:
            sys.exit(1)
        else:
            return {}

    return json_response


def add_language(amara_id, lang, is_original, amara_headers):

    url = AMARA_BASE_URL + 'api/videos/'+amara_id+'/languages/'
    body = { 
        'language_code': lang,
        'subtitles_complete': False,  # To be uploaded later
        'is_primary_audio_language': is_original
        }
    try:
        r= requests.post(url, data=json.dumps(body), headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        eprint(e,"in amara_api::add_language")
        sys.exit(1)

    return json_response


def check_language(amara_id, lang, amara_headers, url=0):
    is_lang_present = False
    sub_version = 0
    body = {
            "limit": 10
            }
    if url == 0:
        url = AMARA_BASE_URL+'/api/videos/'+amara_id+'/languages/'
    try:
        r = requests.get(url,params=body, headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        eprint(e,"in amara_api::check_language")
        eprint(url)
        sys.exit(1)

    for obj in json_response['objects']:
        if obj['language_code'] == lang:
            is_lang_present = True
            sub_version = len(obj['versions'])
            break
    
    if is_lang_present == False and next != None:
        return check_language(amara_id, lang, amara_headers, url= r.json()["meta"]["next"])
    else:
        # DH temporary, print number of languages
        with open("numlang.dat","a") as f:
            f.write(str(json_response["meta"]["total_count"])+'\n')
        return (is_lang_present, sub_version)


def upload_subs(amara_id, lang, is_complete, subs, sub_format, amara_headers):
    url = AMARA_BASE_URL + 'api/videos/'+amara_id+'/languages/'+lang+'/subtitles/'
    body = { 
        'subtitles': subs,
        'sub_format': sub_format,
        'language_code': lang,
        'is_complete': is_complete,   # Warning, this is deprecated
        #'action': "Publish"
        }
    try:
        r = requests.post(url, data=json.dumps(body), headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        eprint(e,"in amara_api::upload_subs")
        sys.exit(1)

    return json_response


def download_subs(amara_id, lang, sub_format, amara_headers ):
    url = AMARA_BASE_URL+'/api/videos/'+amara_id+'/languages/'+lang+'/subtitles/?format='+sub_format
    body = { 
        'language_code': lang,
        'video-id': amara_id
        }
    try:
        r = requests.get(url, data=json.dumps(body), headers=amara_headers )
        r.raise_for_status()
    except requests.HTTPError as e:
        eprint(e, " in amara_api::download_subs")
        sys.exit(1)


    # We should always use "check_language" before we atempt to download
    # This is just that we do not copy empty subtitles
    # Maybe we could give higher treshold.
    if len( r.text ) < 20:
        eprint("ERROR: Something shitty happened, the length of subtitles is too short.")
        eprint("This is what I got from Amara.")
        epprint(r.text)
        answer = asnwer_me("Should I proceed?")
        if not answer:
            sys.exit(1)

    return r.text

def compare_videos(amara_id1, amara_id2, amara_headers):
    url1 = AMARA_BASE_URL+'api/videos/'+amara_id1
    url2 = AMARA_BASE_URL+'api/videos/'+amara_id2

    try:
        r = requests.get(url1, headers=amara_headers )
        r.raise_for_status()
        len1 = r.json()['duration']
    except requests.HTTPError as e:
        eprint(e," in amara_api::compare_videos")
        sys.exit(1)

    try:
        r = requests.get(url2, headers=amara_headers )
        r.raise_for_status()
        len2 = r.json()['duration']
    except requests.HTTPError as e:
        eprint(e," in amara_api::compare_videos")
        sys.exit(1)


    if len1 == len2:
        return True
    
    else:
        print('The length of the first video is:'+str(len1))
        print('The length of the second video is:'+str(len2))
        answer = answer_me("The lengths of the two videos are different. Should I proceed anyway?")
        if answer:
            return False
        else:
            sys.exit(1)



