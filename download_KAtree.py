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

def load_tree(content):
    if content not in content_types:
        return load_obj_bin("KAtree_"+content+"_bin")
    else:
        return load_obj_bin("KAtree_"+content+"_bin")
        print("Invalid content type!", content)
        print("Possibilities are:", content_types)
#        exit(0)

def print_children_titles(content_tree):
    for child in content_tree["children"]:
       pprint(child['title'])

def find_topic(tree, title):
    if "children" not in tree.keys() or len(tree['children']) == 0:
        return None
    for c in tree['children']:
        if c['title'] == title:
            return c
    # Breadth first search
    for c in tree['children']:
        result = find_topic(c, title)
        if result is not None:
           return result
    # Depth first search
    #    else:
    #        result = find_topic(c, title)
    #        if result is not None:
    #            return result
    return None


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
            save_obj_text(tree, "KAtree_"+what+"_txt")
            save_obj_bin(tree, "KAtree_"+what+"_bin")
        else:
            tree = load_tree(what)
    else:
        tree = load_obj_bin("KAtree_"+what+"_bin")

    if  what == 'video' or what == 'all':
        # We are using set to get rid of duplicates
        videos = set()
 
        kapi_tree_print_videoids(tree, videos)
 
        with open("allvideos_ids.dat","w") as out:
            for v in videos:
                out.write(v)


    if subject_title == 'root':
        subtree = tree
    else:
        subtree = find_topic(tree, subject_title)

    # The following is helpful to determine where things are
    if lst:
        if subtree is not None:
            print_children_titles(subtree)
            sys.exit(0)
        else:
            print("ERROR: Could not find topic titled: "+subject_title)
            sys.exit(1)
    
    # Making large table of data for a given subject
    # Note that this unfortunately only work at the subject level,
    # Not for e.g. individual topics or tutorials
    # We should fix function kapi_tree_print_full to be more general
    content = []
    date = time.strftime("%d%m%Y")
    
    kapi_tree_print_full(subtree, content)

    filename = what+"_"+subject_title+"_"+date+".txt"
    with open(filename,"w") as f:
        for c in content:
            f.write(c)

