#!/usr/bin/env python3
import json, sys
import requests 
from pprint import pprint

#SERVER_URL = 'http://bg.khanacademy.org'
SERVER_URL = 'http://khanacademy.org'
TP_URL = 'https://www.khanacademy.org/translations/edit/cs/'
DEFAULT_API_RESOURCE = '/api/v1/'
# Version 2 is not documented, here used only for topic tree
# But apparently does not even fetch the whole tree, so new code will be needed
#DEFAULT_API_RESOURCE = '/api/v2/'
API2 = '/api/v2/'

kapi_headers = {
   'Content-Type': 'application/json',
   'format': 'json'
}


def kapi_check_video(YTID):
    url = SERVER_URL + DEFAULT_API_RESOURCE + 'videos/'  + YTID
    try:
        r = requests.get(url, headers=kapi_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)

    return json_response

def kapi_download_topic(topic):
    url = SERVER_URL + DEFAULT_API_RESOURCE + 'topic/'  + topic
    try:
        r = requests.get(url, headers=kapi_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)

    return json_response


def kapi_download_topictree(what='all'):
    """Argument can be 'video', 'exercise', 'article', 'topic' or 'all' """

    if what == 'article':
        url = SERVER_URL + API2 + 'topics/topictree'
    else:
        url = SERVER_URL + DEFAULT_API_RESOURCE + 'topictree'

    etagfile = "KAtree_"+what+"_etag.dat"
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

    if what != "all" and what != "video":
        body = {
            "kind": what
        }
    else:
        body = {}

    try:
        r = requests.get(url, params=body, headers=ka_headers )
        r.raise_for_status()
        if r.status_code == 304:
            print("Topic tree up-to-date")
            print("If you want to download anyway, remove file "+etagfile+" and run again.")
            return None
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)

    # It seems that etag is not present in v2 api
    if "etag" in r.headers:
        with open(etagfile, "w") as f:
            f.write(r.headers["etag"])
    else:
        print("Etag not found in response header.")
        pass

    return json_response


def kapi_tree_print_videoids(tree, out_set):
    if tree["kind"] == "Video":
        out_set.add(tree["youtube_id"]+'  '+tree["readable_id"]+'\n')
    elif tree["kind"] == "Topic":
        if len(tree["children"]) <= 0:
            # This can happen if Topic includes only Exercises or Articles
           return
        for c in tree["children"]:
            kapi_tree_print_videoids(c, out_set)


def kapi_tree_print_full(tree, out_list):
    delim = ';'
    if tree["kind"] == "Topic":

        if len(tree["children"]) <= 0:
            # This can happen if Topic includes only Exercises or Articles
            # Articles seems to be topics as well
           out_list.append('\n')
           return
        for c in tree["children"]:
            if c['kind'] == "Topic":
                title = c['title']
                if title.split()[0] != "Skill":
                    #out_list.append(title+'\t'+c['description']+'\n')
                    # Dirty hack to align columns
                    if c['render_type'] == 'Tutorial' and out_list[-1][-1] == '\n':
                        out_list.append(delim+title+delim)
                    else:
                        out_list.append(title+delim)
            kapi_tree_print_full(c, out_list)

    else:

        title = tree['title']
        desc = tree['description']
        if desc is None:
            desc = " "
        else:
            desc = desc.expandtabs(0).replace('\n',' ')
        ka_url = tree['ka_url']

        # These are useless
        if "keywords" in tree:
            keywords = tree['keywords']
        else:
            keywords = " "

        if tree["kind"] == "Video":
            ytid = tree["youtube_id"]
            # yt_url is not present in all videos, we will make our own
            #yt_url = tree['url']
            yt_url = 'https://www.youtube.com/watch?v='+ytid
            if 'mp4' in tree['download_urls']:
                download_urls = tree['download_urls']['mp4']
            else:
                download_urls = " "
            dur = str(tree['duration'])
        else:
            ytid = " "
            yt_url = " "
            download_urls = " "
            dur = " "
 
        # This does not work, google sheets interprets this as a text
        link_ka = 'HYPERLINK("'+ka_url+'","link")'
        link_yt = 'HYPERLINK("'+yt_url+'","link")'

        # TODO add Amara link - maybe we don't need auth for that

        # Dirty hack to make columns aligned
        if out_list[-1][-1] == '\n':
            table_row = delim+delim
        else:
            table_row = ''

        table_row = table_row + title+delim+ka_url

        # For videos, add links to YouTube and video duration
        if tree["content_kind"] == "Video":
            table_row = table_row + delim + ytid + delim + yt_url + delim + dur

        # For exercises, add link to Translation Portal
        # Currently hard-coded for MATH, don't know how to generalize it :(
        if tree["content_kind"] == "Exercise":
            tp_link = delim+TP_URL+'/math/'+tree['node_slug']
            table_row = table_row + tp_link

        table_row = table_row + '\n'

        out_list.append(table_row)

