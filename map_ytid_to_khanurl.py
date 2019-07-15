#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time

# This is basically a specialized faster version of map_ytid_to_khandata.py
# We take the data from previously downloaded full topic tree
# This is faster then going video-by-video, depending on how many videos you have
# Unfortunately, due to a bug in KA API, this does not work for certain attributes like
# translated_title

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for mapping YouTube IDs to KA URLs to Crowdin WYSIWYG editor." 
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Print full tree for a given domain/subject.')
   parser.add_argument('-l','--lang', dest='lang', default='en', help='Language of LTT.')
   return parser.parse_args()

if __name__ == "__main__":

    opts = read_cmd()
    infile = opts.input_file
    subject_title  = opts.subject

    # List ytids may also contain filenames
    ytids = []
    # Reading file with YT id's
    with open(infile, "r") as f:
        for line in f:
            y = line.split()
            if len(y) != 0:
                ytids.append(y[0])
            else:
                ytids.append(None)

    khan_tree = KhanContentTree(opts.lang, 'video')
    tree = khan_tree.get()

    if subject_title == 'root':
        subtree = tree
    else:
        subtree = find_ka_topic(tree, subject_title)

    videos = []
    for ytid in ytids:
        if ytid is not None:
            v = find_video_by_youtube_id(subtree, ytid)
        if v:
            videos.append(v)
        else:
            videos.append(ytid)

    for v in videos:
        try:
            print(v['ka_url'].replace('www', 'translate'))
        except:
            print(v)

