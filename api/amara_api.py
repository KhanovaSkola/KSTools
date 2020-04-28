#!/usr/bin/env python3
import json, sys, os
import requests 
from pprint import pprint
from utils import answer_me, eprint

class Amara:

    AMARA_BASE_URL = 'https://amara.org'
    EXIT_ON_HTTPERROR  = False
    
    # File 'apifile' should contain only one line with your Amara API key and (optionally) Amara username.
    # Amara API can be found in Settins->Account-> API Access (bottom-right corner)
    AMARA_API_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../SECRETS/amara_api_credentials.txt"))

    def __init__(self):
        api_key = self._get_api_key()
        self.headers = {
            'Content-Type': 'application/json',
            'X-api-key': api_key,
            'format': 'json'
        }
        # Persistent connection via requests.Session()
        # http://docs.python-requests.org/en/master/user/advanced/
        self.session = requests.Session()

    def _get_api_key(self):
        """Reads and returns user API key from pre-defined file"""
        with open(self.AMARA_API_FILE, "r") as f:
            cols = f.read().split()
            if len(cols) > 2:
                print("ERROR: Invalid input in file %s" % AMARA_API_FILE)
                sys.exit(1)
            elif len(cols) == 2:
                # NOTE(danielhollas): amara_username is optional
                # It is no longer required in amara_headers so we'll only print it here
                # but do not return
                amara_username = cols[1]
                print('Using Amara username: ' + amara_username)
 
            amara_api_key = cols[0]
 
        return amara_api_key

    def _get(self, url, body):
        try:
            r = self.session.get(url, params = body, headers = self.headers)
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            eprint('Error for video', url)
            eprint(e)
            eprint("Response:", r)
            if self.EXIT_ON_HTTPERROR:
                sys.exit(1)
            else:
                return {}


    def _post(self, url, body):
        try:
            r = self.session.post(url, data = json.dumps(body), headers = self.headers)
            r.raise_for_status()
            # TODO: Check what type of response we got (JSON or not?)
            return r.json()
 
        except requests.HTTPError as e:
            eprint('ERROR for video %s\n' % url)
            eprint("Response:", r)
            if self.EXIT_ON_HTTPERROR:
                sys.exit(1)
            else:
                return {}
 

    def check_video(self, video_url):
        url = "%s/api/videos/" % self.AMARA_BASE_URL
        body = { 
            'video_url': video_url
            }
        return self._get(url, body)


    def add_video(self, video_url, video_lang):
        url = "%s/api/videos/" % self.AMARA_BASE_URL
        body = {
            'video_url': video_url,
            'primary_audio_language_code': video_lang
            }
        
        return self._post(url, body)


    def add_language(self, amara_id, lang, is_original):
        url = "%s/api/videos/%s/languages/" %(self.AMARA_BASE_URL, amara_id)
        body = { 
            'language_code': lang,
            'subtitles_complete': False,  # To be uploaded later
            'is_primary_audio_language': is_original
            }
        return self._get(url, body)


    def check_language(self, amara_id, lang, url=None):
        is_lang_present = False
        sub_version = 0
        body = {
               "limit": 10
               }
 
        if url is None:
            url = "%s/api/videos/%s/languages/" % (self.AMARA_BASE_URL, amara_id)
 
        json_response = self._get(url, body)
 
        for obj in json_response['objects']:
            if obj['language_code'] == lang:
                is_lang_present = True
                sub_version = len(obj['versions'])
                break
 
        # Paginated output if there are many languages
        next = json_response['meta']['next']
       
        if is_lang_present == False and next != None:
            return check_language(amara_id, lang, url = next)
        else:
            return (is_lang_present, sub_version)


    def upload_subs(self, amara_id, lang, subtitles_complete, subs, sub_format):
        url = "%s/api/videos/%s/languages/%s/subtitles/" % (self.AMARA_BASE_URL, amara_id, lang)
        body = { 
            'subtitles': subs,
            'sub_format': sub_format,
            'language_code': lang,
            }
        if subtitles_complete:
            body['action'] = 'publish'
 
        return self._post(url, body)


    def download_subs(self, amara_id, lang, sub_format):
        url = "%s/api/videos/%s/languages/%s/subtitles/?format=%s" % (self.AMARA_BASE_URL, amara_id, lang, sub_format)
        body = { 
            'language_code': lang,
            'video-id': amara_id
            }
        # Cannot use _get() because subtitles are not in json format
        # Maybe we could somehow handle that in _get as well though
        try:
            r = self.session.get(url, data=json.dumps(body), headers = self.headers )
            r.raise_for_status()
        except requests.HTTPError as e:
            eprint(e, " in amara_api::download_subs")
            sys.exit(1)
 
        # We should always use "check_language" before we atempt to download
        # This is just that we do not copy empty subtitles
        # Maybe we could give higher treshold.
        if len(r.text) < 20:
            eprint("ERROR: Something shitty happened, the length of subtitles is too short.")
            eprint("This is what I got from Amara.")
            epprint(r.text)
            answer = asnwer_me("Should I proceed?")
            if not answer:
                sys.exit(1)
 
        return r.text


    # TODO: Not tested
    def compare_videos(self, amara_id1, amara_id2):
        url1 = "%s/api/videos/%s/" % (self.AMARA_BASE_URL, amara_id1)
        url2 = "%s/api/videos/%s/" % (self.AMARA_BASE_URL, amara_id2)
        body = { 
            }
        json_response = self._get(url1, body)
        len1 = json_response['duration']
        json_response = self._get(url2, body)
        len2 = json_response['duration']
 
        if len1 == len2:
            return True
        else:
            # TODO: Push this logic out of here!
            print('The length of the first video is:' + str(len1))
            print('The length of the second video is:' + str(len2))
            answer = answer_me("The lengths of the two videos are different. Should I proceed anyway?")
            if answer:
                return False
            else:
                sys.exit(1)


    def add_primary_audio_lang(self, amara_id, video_lang):
        url = "%s/api/videos/%s/" % (self.AMARA_BASE_URL, amara_id)
        body = { 
            'primary_audio_language_code': video_lang
            }
        try:
            # TODO: Make put into _put
            r = self.session.put(url, data = json.dumps(body), headers = self.headers)
            r.raise_for_status()
            json_response = r.json()
        except requests.HTTPError as e:
            eprint('ERROR for video',video_url)
            eprint(e," in amara_api::add_primary_video_lang")
            if EXIT_ON_HTTPERROR:
                sys.exit(1)
            else:
                return {}
 
        return json_response

