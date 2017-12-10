#!/usr/bin/env python3
import json, sys
import requests 
from pprint import pprint
import youtubedl_common
from xml.etree import ElementTree


YTAPI_VERSION = 'v3/'
YTAPI_BASE_URL = 'https://www.googleapis.com/youtube/'+YTAPI_VERSION
API_KEY = 'AIzaSyBtZJiEfa42lvDHePwJ8Fvkhr-VwgJQOj0'

#https://stackoverflow.com/questions/23665343/get-closed-caption-cc-for-youtube-video

yt_headers = {
   'Content-Type': 'application/json',
#   'X-api-key': API_KEY,
   'format': 'json'
}

def yt_list_langs(ytid):
    response = requests.get('https://video.google.com/timedtext?hl=en&type=list&v=%s' % ytid)

#  use only regexps
    tree = ElementTree.fromstring(response.content)
    root = tree.getroot()
   # except as e:
   #     print("ERROR during downloading YT lang list.")
   #     raise(e)
   #     return []

    pprint(root)
    sys.exit(1)

    sub_lang_list = []
    for track in subs_doc.findall('track'):
        lang = track.attrib['lang_code']
        sub_lang_list.append(lang)

def yt_sub_upload(ytid, lang, subs, publish):
    pass

def yt_sub_download(ytid, lang, subs, caption_id):
    pass

def get_playlist_items(pl_id):
    url = YTAPI_BASE_URL+'playlistItems'
    body = { 
        'part': "snippet",
        'playlistId': pl_id,
        'maxResults': 50,
        'key': API_KEY
        }
    try:
        r = requests.get(url, params=body, headers=yt_headers )
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

def print_playlist_items(pl_id):
    pl = get_playlist_items(pl_id)
    print(pl)

def print_playlist_ytids(pl_id):
    pl = get_playlist_items(pl_id)
    pginfo = pl['pageInfo']
    max_res = pginfo['resultsPerPage']
    total_res = pginfo['totalResults']
    if max_res <= total_res:
        print("Whoops: the playlists has more than 50 items! Not implemented!")
    print('#\t',pl['pageInfo'])

    for vid in pl['items']:
        if vid['snippet'][ 'resourceId']['kind'] == 'youtube#video':
            print(vid['snippet'][ 'resourceId']['videoId']+'\t'+ vid['snippet'][ 'title'])

if __name__ == "__main__":

    plid1 = ('PLC51FJvpvRvxAdEO8t6mLXt2m0UMxZrnI','Computing - JS-Drawing')
    plid2 = ('PLC51FJvpvRvyK3n1d-Kth7ldHO__Tpygr','Computing - HTML/CSS')
    plid3 = ('PLC51FJvpvRvzZEjyNmwOG9DQ9xqKNecUr','Computing - Jquery')
    plid4 = ('PLC51FJvpvRvwWfYsQMq1sCmVL-hEfDEpY','Computing - SQSL')
    plid5 = ('PLC51FJvpvRvwPoOb3n80zppJIgWDf1wvQ','Computing - HTML/JS')

    plid6 = ('PLB632EC24182B4D40', 'Katie Gimbar Flipped Classroom - FAQ')
    plid7 = ('PL10g2YT_ln2iI46Zt3OdzgP_E9ept6OU9', 'Edutopia top 10 - 2015')

    plids = [plid1, plid2, plid3, plid4, plid5]
    plids = [plid6, plid7]
#    print_playlist_items(plid6)

    for plid in plids:
        print('#\t', plid[1])
        print_playlist_ytids(plid[0])


