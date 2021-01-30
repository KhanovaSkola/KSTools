#!/usr/bin/env python3
import json, sys, os
import requests 
from pprint import pprint

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Amara:

    AMARA_BASE_URL = 'https://amara.org'
    EXIT_ON_HTTPERROR  = True
    
    # File 'apifile' should contain only one line with your Amara API key and Amara username.
    # Amara API can be found in Settins->Account-> API Access (bottom-right corner)
    AMARA_API_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../SECRETS/amara_api_credentials.txt"))

    def __init__(self, username):
        self.username = username
        api_key = self._get_api_key(username)
        self.headers = {
            'Content-Type': 'application/json',
            'X-api-key': api_key,
            'format': 'json'
        }
        # Persistent connection via requests.Session()
        # http://docs.python-requests.org/en/master/user/advanced/
        self.session = requests.Session()

    def _get_api_key(self, username):
        """Reads API key from pre-defined file for a given username"""
        print("Using Amara username %s" % username)
        with open(self.AMARA_API_FILE, "r") as f:
            for line in f:
                cols = line.strip().split()
                if len(cols) != 2:
                    eprint("ERROR: Invalid input in file %s" % self.AMARA_API_FILE)
                    sys.exit(1)
                api_key = cols[0]
                if cols[1] == username:
                    return api_key

        eprint("ERROR: Could not find API key for username %s" % username)
        sys.exit(1)

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
            eprint(r)
            if self.EXIT_ON_HTTPERROR:
                sys.exit(1)
            else:
                return r

    def _put(self, url, body):
        try:
            r = self.session.put(url, data = json.dumps(body), headers = self.headers)
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            eprint('ERROR: PUT request %s failed\n' % url)
            eprint(r)
            if self.EXIT_ON_HTTPERROR:
                sys.exit(1)
            else:
                return r

    def _delete(self, url):
        try:
            r = self.session.delete(url, headers = self.headers)
            r.raise_for_status()
            # NOTE: we're currently using this only to delete subtitle request,
            # in which case the server does not return body, just 204 status.
            # So we just return the HTTP code here
            return r.status_code
        except requests.HTTPError as e:
            eprint('ERROR: DELETE request to %s failed\n' % url)
            eprint(r)
            if self.EXIT_ON_HTTPERROR:
                sys.exit(1)
            else:
                return r.status_code
 

    def check_video(self, video_url, team = None):
        url = "%s/api/videos/" % self.AMARA_BASE_URL
        body = { 
            'video_url': video_url
            }
        if team is not None:
            body['team'] = team
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
            return self.check_language(amara_id, lang, url = next)
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
            body['action'] = 'endorse'
 
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
            print('ERROR: The lengths of the two videos are different.')
            print('The length of the first video is:' + str(len1))
            print('The length of the second video is:' + str(len2))
            return False

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

    def list_actions(self, amara_id, lang):
        url = "%s/api/videos/%s/languages/%s/subtitles/actions/" \
                % (self.AMARA_BASE_URL, amara_id, lang)
        body = {}
        return self._get(url, body)


    def perform_action(self, action, amara_id, lang):
        url = "%s/api/videos/%s/languages/%s/subtitles/actions/" \
                % (self.AMARA_BASE_URL, amara_id, lang)
        body = {'actions': action}
        response = self._get(url, body)
        return response

    def list_subtitle_requests(self, amara_id, lang, team):
        url = "%s/api/teams/%s/subtitle-requests/" \
                % (self.AMARA_BASE_URL, team)
        body = {
           'video': amara_id,
           'language': lang,
        }
        return self._get(url, body)

    def create_subtitle_request(self, amara_id, lang, team):
        url = "%s/api/teams/%s/subtitle-requests/" \
                % (self.AMARA_BASE_URL, team)
        body = {
           'video': amara_id,
           'language': lang,
        }
        return self._post(url, body)


    def delete_subtitle_request(self, job_id, team):
        """https://apidocs.amara.org/#delete-a-request"""
        url = "%s/api/teams/%s/subtitle-requests/%s/" \
                % (self.AMARA_BASE_URL, team, job_id)
        body = {
        }
        return self._delete(url)

    def assign_subtitler(self, job_id, team):
        url = "%s/api/teams/%s/subtitle-requests/%s/" \
                % (self.AMARA_BASE_URL, team, job_id)
        body = {
           'subtitler': self.username,
        }
        return self._put(url, body)

    def assign_reviewer(self, job_id, team):
        url = "%s/api/teams/%s/subtitle-requests/%s/" \
                % (self.AMARA_BASE_URL, team, job_id)
        body = {
           'reviewer': self.username,
        }
        return self._put(url, body)

    def unassign_reviewer(self, job_id, team):
        url = "%s/api/teams/%s/subtitle-requests/%s/" \
                % (self.AMARA_BASE_URL, team, job_id)
        body = {
           'reviewer': None,
        }
        return self._put(url, body)

    def mark_subtitles_complete(self, job_id, team):
        url = "%s/api/teams/%s/subtitle-requests/%s/" \
                % (self.AMARA_BASE_URL, team, job_id)
        body = {
           'work_status': 'complete',
        }
        return self._put(url, body)

    # https://apidocs.amara.org/#languages
    def list_all_amara_languages(self):
        url = "%s/api/languages/" % (self.AMARA_BASE_URL)
        body = {}
        return self._get(url, body)
