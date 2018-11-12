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
content_types = ['video', 'article', 'exercise', 'topic', 'tutorial', 'all']


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

    if what == "tutorial" or what == "topic":
        download_type = 'video'
    else:
        download_type = what
    if download:
        tree = kapi_download_topictree(download_type)
        if tree != None:
            save_obj_text(tree, "KAtree_" + download_type + "_txt")
            save_obj_bin(tree, "KAtree_" + download_type + "_bin")
        else:
            tree = load_ka_tree(download_type)
    else:
        #tree = load_obj_bin("KAtree_"+download_type+"_bin")
        tree = load_ka_tree(download_type)

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
        subtree = find_ka_topic(tree, subject_title)

    # The following is helpful to determine where things are
    if lst:
        if subtree is not None:
            print("Printing dictionary for topic ", subject_title)
            print_dict_without_children(subtree)
            print("=============================")
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
    
    if what == 'tutorial':
        kapi_tree_print_tutorials(subtree, content)
    else:
        kapi_tree_print_full(subtree, content)

    filename = what+"_"+format_filename(subject_title)+"_"+date+".csv"
    with open(filename, "w", encoding = 'utf-8') as f:
        for c in content:
            f.write(c)

