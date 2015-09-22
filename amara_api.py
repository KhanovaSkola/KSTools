#!/usr/bin/env python
import requests, json
from pprint import pprint

# TODO
# the try - except code is probably not working properly
# In general, error handling is probably not done well.

AMARA_BASE_URL = 'https://www.amara.org/'


def check_video(video_url, amara_headers):
    url = AMARA_BASE_URL + 'api/videos/'
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


def add_video(video_url, video_lang, amara_headers):
    url = AMARA_BASE_URL + 'api/videos/'
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


def add_language(amara_id, lang, is_original, amara_headers):

    url = AMARA_BASE_URL + 'api/videos/'+amara_id+'/languages/'
    body = { 
        'language_code': lang,
        'subtitles_complete': False,  # To be uploaded later
        'is_primary_audio_language': is_original
        }
    try:
        response = requests.post(url, data=json.dumps(body), headers=amara_headers )
        json_response = response.json()
    except requests.HTTPError as e:
        print e
        sys.exit(1)

    return json_response


def check_language(amara_id, lang, amara_headers):
    is_lang_present = False
    sub_version = 0
    url = AMARA_BASE_URL+'/api/videos/'+amara_id+'/languages/'
    try:
        r = requests.get(url, headers=amara_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print e
        sys.exit(1)

    for obj in json_response['objects']:
        if obj['language_code'] == lang:
            is_lang_present = True
            sub_version = len(obj['versions'])
            break

    return (is_lang_present, sub_version)


def upload_subs(amara_id, lang, is_complete, subs, sub_format, amara_headers):
    url = AMARA_BASE_URL + 'api/videos/'+amara_id+'/languages/'+lang+'/subtitles/'
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
        json_response = response.json()
    except requests.HTTPError as e:
        print e
        sys.exit(1)

    return json_response

def download_subs():
    pass


