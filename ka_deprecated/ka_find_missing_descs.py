#!/usr/bin/env python3
from kapi import *
import utils
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for finding KA content without descriptions."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-s','--subject', dest='subject', default = 'root', help = 'Link given course.')
   parser.add_argument('-c','--content', dest='content', required = True, help = 'Content kind: video|exercise')
   return parser.parse_args()

# Currently, article type does not seem to work.
CONTENT_TYPES = ['video', 'exercise']


def print_slugs_without_descriptions(content):
    unique_content_ids = set()

    for c in content:

        if c['id'] in unique_content_ids:
            continue
        else:
            unique_content_ids.add(c['id'])

        if c['translated_description'] is None:
            #print(c['node_slug'], 'WARNING: Empty description, returning None')
            print(c['node_slug'])
        elif not c['translated_description']:
            #print(c['node_slug'], 'WARNING: Empty description!')
            print(c['node_slug'])


if __name__ == '__main__':

    opts = read_cmd()
    topic = opts.subject
    content_type = opts.content.lower()

    if content_type not in CONTENT_TYPES:
        print("ERROR: content argument: ", opts.content)
        print("Possibilities are: ", CONTENT_TYPES)
        exit(1)

    khan_tree = KhanContentTree('en', content_type)
    tree = khan_tree.get()
    if topic != 'root':
        subtree = find_ka_topic(tree, topic)
    else:
        subtree = tree
    if not subtree:
        print("ERROR: Could not find subtree for topic: %s\n" % (topic))
        sys.exit(1)

    content = []
    kapi_tree_get_content_items(subtree, content, content_type)
    print_slugs_without_descriptions(content)


