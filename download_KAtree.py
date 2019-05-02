#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time


def read_cmd():
   """Function for reading command line options."""
   desc = "Script for downloading Khan Academy content tree." 
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-c','--content', dest='content_type', required = True, help='Which kind of content should we download? Options: video|exercise|article|topic')
   parser.add_argument('-l', '--lang', dest='lang', default = 'en', help='Language of the topic tree. (US by default)')
   return parser.parse_args()

# Currently, article type does not seem to work.
AVAILABLE_CONTENT_TYPES = ['video', 'article', 'exercise', 'topic', 'tutorial', 'all']

if __name__ == "__main__":

    opts = read_cmd()

    if opts.content_type not in AVAILABLE_CONTENT_TYPES:
        print("ERROR: invalid content type argument:", opts.content_type)
        print("Available:", AVAILABLE_CONTENT_TYPES)
        exit(1)

    if opts.content_type == "tutorial" or opts.content_type == "topic":
        download_type = 'video'
    else:
        download_type = opts.content_type

    khan_tree = KhanContentTree(opts.lang, download_type)
    kapi = KhanAPI(opts.lang)
    tree = kapi.download_topic_tree(download_type)
    if tree is not None:
        khan_tree.save(tree)
        print("Successfully downloaded Khan %s topic tree for locale %s" % (opts.content_type, opts.lang))
    else:
        print("ERROR: Could not download topic tree for locale " + opts.lang)
        sys.exit(1)

