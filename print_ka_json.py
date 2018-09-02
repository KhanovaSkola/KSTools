#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time


def read_cmd():
   """Function for reading command line options."""
   desc = "Program for downloading and printing Khan Academy content tree." 
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-d','--download',dest='download',default=False,action="store_true", help='Download most up-to-date full tree?')
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Print full tree for a given domain/subject.')
   parser.add_argument('-c','--content', dest='content', default="all", help='Which kind of content should we download? Options: video|exercise|article|topic')
   parser.add_argument('-l','--list', dest='list', default=False,action="store_true", help='Only list topic names within given domain/subject/topic.')
   return parser.parse_args()

# Currently, article type does not seem to work.
content_types = ["video", "article", "exercise", "topic","all"]


def print_children_titles(content_tree):
    for child in content_tree["children"]:
       pprint(child['title'])

def print_dict_without_children(dictionary):
    for k in dictionary.keys():
        if k != 'children':
            print(k, dictionary[k])

if __name__ == "__main__":

    opts = read_cmd()
    download = opts.download
    subject_title  = opts.subject
    what = opts.content.lower()
    lst = opts.list


    if what not in content_types:
        print("ERROR: content argument:", opts.content)
        print("Possibilities are:", content_types)
        exit(1)

    if download:
        tree = kapi_download_topictree(what)
        if tree != None:
            #save_obj_text(tree, "KAtree_"+what+"_txt")
            save_obj_bin(tree, "KAtree_"+what+"_bin")
        else:
            tree = load_ka_tree(what, content_types)
    else:
        #tree = load_obj_bin("KAtree_"+what+"_bin")
        tree = load_ka_tree(what, content_types)

    if  what == 'video' or what == 'all':
        # We are using set to get rid of duplicates
        videos = set()
 
        kapi_tree_get_content_items(tree, videos)
 
        with open("videos.json","w", encoding = 'utf-8') as out:
            for v in videos:
                out.write(v)


