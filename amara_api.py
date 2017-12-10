#!/usr/bin/env python3
import json, sys
import requests 
from pprint import pprint
from utils import *

AMARA_BASE_URL = 'https://amara.org/'
EXIT_ON_HTTPERROR  = False

# Additional parameter 's' is the request Session object
# which maintains persistent connection
# http://docs.python-requests.org/en/master/user/advanced/

def my_get(url, body, amara_headers, session=None):
    try:
        if session is None:
            r = requests.get(url, params=body, headers=amara_headers )
        else:
            r = session.get(url, params=body, headers=amara_headers )

        r.raise_for_status()
        return r.json()

    except requests.HTTPError as e:
        eprint('Error for video',url)
        eprint(e)
        try:
            eprint(r.json())
        except:
            # Catch exception when r.json is empty
            pass
        if EXIT_ON_HTTPERROR:
            sys.exit(1)
        else:
            return {}


def my_post(url, body, amara_headers, session=None):
    try:
        if session is None:
            r = requests.post(url, data=json.dumps(body), headers=amara_headers )
        else:
            r = session.post(url, data=json.dumps(body), headers=amara_headers )

        r.raise_for_status()
        return r.json()

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


def check_video(video_url, amara_headers, s=None):
    url = AMARA_BASE_URL + 'api/videos/'
    body = { 
        'video_url': video_url
        }

    json_response = my_get(url, body, amara_headers, session=s)

    return json_response


def add_video(video_url, video_lang, amara_headers, s=None):
    url = AMARA_BASE_URL + 'api/videos/'
    body = {
        'video_url': video_url,
        'primary_audio_language_code': video_lang
        }
    
    json_response = my_post(url, body, amara_headers, session=s)

    return json_response


def add_language(amara_id, lang, is_original, amara_headers, s=None):

    url = AMARA_BASE_URL + 'api/videos/'+amara_id+'/languages/'
    body = { 
        'language_code': lang,
        'subtitles_complete': False,  # To be uploaded later
        'is_primary_audio_language': is_original
        }

    json_response = my_get(url, body, amara_headers, session=s)

    return json_response


def check_language(amara_id, lang, amara_headers, s=None, url=0):
    is_lang_present = False
    sub_version = 0
    body = {
            "limit": 10
            }

    if url == 0:
        url = AMARA_BASE_URL+'api/videos/'+amara_id+'/languages/'

    json_response = my_get(url, body, amara_headers, session=s)

    for obj in json_response['objects']:
        if obj['language_code'] == lang:
            is_lang_present = True
            sub_version = len(obj['versions'])
            break

    # Paginated output if there are many languages
    next = json_response['meta']['next']
    
    if is_lang_present == False and next != None:
        return check_language(amara_id, lang, amara_headers, s=s, url= next)
    else:
        return (is_lang_present, sub_version)


def upload_subs(amara_id, lang, is_complete, subs, sub_format, amara_headers,s=None):
    url = AMARA_BASE_URL + 'api/videos/'+amara_id+'/languages/'+lang+'/subtitles/'
    body = { 
        'subtitles': subs,
        'sub_format': sub_format,
        'language_code': lang,
        'is_complete': is_complete,   # Warning, this is deprecated
        #'action': "Publish"
        }

    json_response = my_post(url, body, amara_headers, session=s)

    return json_response


def download_subs(amara_id, lang, sub_format, amara_headers, s=None):
    url = AMARA_BASE_URL+'api/videos/'+amara_id+'/languages/'+lang+'/subtitles/?format='+sub_format
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


def compare_videos(amara_id1, amara_id2, amara_headers, s = None):
    url1 = AMARA_BASE_URL+'api/videos/'+amara_id1+'/'
    url2 = AMARA_BASE_URL+'api/videos/'+amara_id2+'/'

    body = { 
        }

    try:
        json_response = my_get(url1, body, amara_headers, session=s)
        len1 = json_response['duration']
    except requests.HTTPError as e:
        eprint(e," in amara_api::compare_videos")
        sys.exit(1)

    try:
        json_response = my_get(url2, body, amara_headers, session=s)
        len2 = json_response['duration']
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


def add_primary_audio_lang(amara_id, video_lang, amara_headers, session=None):
    url = AMARA_BASE_URL + 'api/videos/'+amara_id+'/'
    body = { 
        'primary_audio_language_code': video_lang
        }
    
    try:
        if session is None:
            r = requests.put(url, data=json.dumps(body), headers=amara_headers )
        else:
            r = session.put(url, data=json.dumps(body), headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        eprint('ERROR for video',video_url)
        eprint(e,"in amara_api::add_primary_video_lang")
        if EXIT_ON_HTTPERROR:
            sys.exit(1)
        else:
            return {}

    return json_response

