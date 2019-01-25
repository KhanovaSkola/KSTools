#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys, os
import requests 
from pprint import pprint
from utils import load_obj_bin, save_obj_bin

# And pass locale in constructor
SERVER_URL = 'https://www.khanacademy.org'
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

_EXIT_ON_HTTP_ERROR = False


class KhanAPI:

    def __init__(self, locale):
        if locale == 'en':
            self.server_url = 'https://www.khanacademy.org'
        else:
            self.server_url = 'https://' + locale + '.khanacademy.org'
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'format': 'json'
        }

    def _get_url(self, url, body = {}):
        try:
            r = self.session.get(url, params = body, headers = self.headers)
            r.raise_for_status()
            return r.json()

        except requests.HTTPError as e:
            eprint('HTTP error for URL: ', url)
            eprint(e)
            try:
                eprint(r.json())
            except:
                # Catch exception when r.json is empty
                pass
            if _EXIT_ON_HTTPERROR:
                sys.exit(1)
            else:
                return {}

    def download_video(self, YTID):
        # Searching by YTID is deprecated but seems to work,
        # even searching by translated_youtube_id
        # Instead_ we should be calling this by readable_id
        url = SERVER_URL + DEFAULT_API_RESOURCE + 'videos/'  + YTID
        json_response = self._get_url(url)
        return json_response


    # TODO: Convert to V2 API
    # It seems that the kind argument does not work?
    # EDIT: It seems that the V2 approach will not work here...
    def download_topic_tree(self, content_type):
        """Content type can be 'video', 'exercise', 'article'"""
 
        #url = SERVER_URL + API2 + 'topics/topictree'
        url = SERVER_URL + DEFAULT_API_RESOURCE + 'topictree'
        body = {
            "kind": content_type
        }
        json_response = self._get_url(url, body)
        return json_response


class KhanContentTree():

    def __init__(self, locale, content_type):
        self.content_tree = None
        self.content_type = content_type
        self.file_name = "khan_tree_" + locale + '_' + self.content_type + "_bin.pkl"

    def save(self, tree):
        save_obj_bin(tree, self.file_name)
        self.content_tree = tree

    def load(self):
        if not os.path.isfile(self.file_name):
            print("ERROR: Could not load content tree from file '%s'" % (self.file_name))
            sys.exit(1)
        self.content_tree = load_obj_bin(self.file_name)

    def get(self):
        if self.content_tree is None:
            self.load()
        return self.content_tree

    # This is a bit of a weird function, maybe we should just get rid of the unique bit
    # and handle uniqueness outside of this function?
    def get_unique_content_data(self, ids, out, keys, tree = None):
        if type(ids) is not set or type(out) is not list:
            print("ERROR: Invalid argument to get_unique_content_data!")
            sys.exit(1)

        if tree is None:
            tree = self.content_tree

        if 'kind' not in tree.keys():
            print("ERROR: Could not find 'kind' attribute among:" )
            print(tree.keys())
            sys.exit(1)

        if tree["kind"].lower() == self.content_type and tree['id'] not in ids:
            ids.add(tree['id'])
            data = {}
            for k in keys:
                data[k] = tree[k]
            out.append(data)

        elif tree["kind"] == "Topic":
            # This can happen if Topic includes only Exercises or Articles
            if len(tree["children"]) <= 0:
                return
            for t in tree["children"]:
                self.get_unique_content_data(ids, out, keys, t)
 

def kapi_download_topic(topic, kind):
    url = SERVER_URL + DEFAULT_API_RESOURCE + 'topic/'  + topic
    if kind == 'video' or kind == 'exercise':
        url += '/' + kind + 's'
    print(url)
    try:
        r = requests.get(url, headers=kapi_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)
    return json_response

def kapi_download_videos_from_topic(topic):
    url = SERVER_URL + DEFAULT_API_RESOURCE + 'topic/'  + topic + ''
    try:
        r = requests.get(url, headers=kapi_headers )
        r.raise_for_status()
        json_response = r.json()
    except requests.HTTPError as e:
        print(e)
        sys.exit(1)

    return json_response


def kapi_tree_print_tutorials(tree, out_list):
    delim = ';'
    if tree["kind"] == "Topic":
        if len(tree["children"]) == 0:
            # This can happen if Topic includes only Exercises or Articles
            # Articles seems to be topics as well
           return
        for c in tree["children"]:
            title = c['title']
            url = 'https://cs.khanacademy.org/translations/edit/cs/'
            url = url + c['slug'] + '/tree/upstream'
            out_list.append(title + delim + url + '\n')
            if c['render_type'] != "Tutorial":
                kapi_tree_print_tutorials(c, out_list)
    return

def kapi_tree_print_full(tree, out_list):
    delim = ';'
    if len(out_list) == 0:
        #out_list.append("SUBJECT"+delim+"TOPIC"+delim+"TUTORIAL"+delim+"TITLE\n")
        out_list.append("\n")
    # Attempting to make Full domain listing work
    #if tree["kind"] == "Topic" and tree["render_type"] == 'Subject':
    #   out_list.append("\n")
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
            yt_url = 'https://www.youtube.com/timedtext_video?v='+ytid
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
        #link_ka = 'HYPERLINK("'+ka_url+'","link")'
        #link_yt = 'HYPERLINK("'+yt_url+'","link")'

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


def find_ka_topic(tree, title):
    if "children" not in tree.keys() or len(tree['children']) == 0:
        return None
    # Breadth first search
    for c in tree['children']:
        if c['title'] == title:
            return c
        result = find_ka_topic(c, title)
        if result is not None:
           return result
    return None

def find_video_by_youtube_id(tree, ytid):
    if "children" not in tree.keys() or len(tree['children']) == 0:
        return None
    # Breadth first search
    for c in tree['children']:
        if 'youtube_id' in c.keys() and c['youtube_id'] == ytid:
            return c
        result = find_video_by_youtube_id(c, ytid)
        if result is not None:
           return result
    return None

def kapi_tree_get_content_items(tree, out, content_type="all"):
    if tree["kind"] != "Topic":
        #if content_type == "all" or content_type == tree["content_kind"].lower():
        if content_type == "all" or content_type == tree["kind"].lower():
            out.append(tree)
        return out

    for c in tree['children']:
        kapi_tree_get_content_items(c, out)

    return out

