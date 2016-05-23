#!/usr/bin/env python3
import json, sys
import requests 
from pprint import pprint

SERVER_URL = 'http://www.khanacademy.org'
DEFAULT_API_RESOURCE = '/api/v1/'

kapi_headers = {
   'Content-Type': 'application/json',
   'format': 'json'
}


def check_video(YTID):
    url = SERVER_URL + DEFAULT_API_RESOURCE + 'videos/'  + YTID
    try:
        r = requests.get(url, headers=kapi_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)

    return json_response

def download_topic(topic):
    url = SERVER_URL + DEFAULT_API_RESOURCE + 'topic/'  + topic
    try:
        r = requests.get(url, headers=kapi_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)

    return json_response


def download_topictree(what='all'):
    """Argument can be "video", "exercise" or "topic" """

    url = SERVER_URL + DEFAULT_API_RESOURCE + 'topictree'

    etagfile = "topictree_etag.dat"
    etag = ""
    try:
        with open(etagfile, "r") as f:
            etag = f.read()
    except: 
        pass

    ka_headers = {
       'Content-Type': 'application/json',
       'format': 'json',
       'If-None-Match':  etag
    }

    if what != "all":
        body = {
            "kind": what
        }

    try:
        r = requests.get(url, params=body, headers=ka_headers )
        r.raise_for_status()
        if r.status_code == 304:
            print("Topic tree up-to-date")
            print("If you want to download anyway, remove file "+etagfile+" and run again.")
            return ""
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)

    with open(etagfile, "w") as f:
        f.write(r.headers["etag"])

    return json_response


def tree_print_videoids(tree, fout):
    if tree["kind"] == "Video":
        fout.write(tree["youtube_id"]+'  '+tree["readable_id"]+'\n')
    elif tree["kind"] == "Topic":
        if len(tree["children"]) <= 0:
            # This can happen if Topic includes only Exercises or Articles
           return
        for c in tree["children"]:
            tree_print_videoids(c, fout)


