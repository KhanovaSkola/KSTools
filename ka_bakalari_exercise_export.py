#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for relinking Khan Content Bakalari NEXT e-learning module."
   parser = argparse.ArgumentParser(description=desc)
#   parser.add_argument('-s','--subject', dest='subject', default='root', help='Relink content for a given domain/subject.')
#   parser.add_argument('-c','--content', dest='content', default='video', help='Which kind of content should we relink? Options: video')
   return parser.parse_args()

CONTENT_TYPES = ['exercise']

if __name__ == '__main__':

    opts = read_cmd()
#    topic_title  = opts.subject
#    content_type = opts.content.lower()
    # Let's just do Math for now
    topic_title = 'math'
    content_type = 'exercise'

    if content_type not in CONTENT_TYPES:
        print("ERROR: content argument: ", opts.content)
        print("Possibilities are: ", CONTENT_TYPES)
        exit(1)

    khan_tree = KhanContentTree('cs', content_type)
    tree = khan_tree.get()

    # Pick just concrete topic from KA tree
    if topic_title != 'root':
        subtree = find_ka_topic(tree, topic_title)
    else:
        subtree = tree

    if not subtree:
        print("ERROR: Could not find subtree for course: %s\n" % (topic_title))
        sys.exit(1)

    content = []
    kapi_tree_get_content_items(subtree, content, content_type)

    unique_content_ids = set()

    # KA API returns unlisted content as well, need to deal with that externally
    listed_content_slugs = read_listed_content_slugs()

    ka = KhanAPI('cs')

    with open('bakalari_khan_export_%s_%s.csv' % (topic_title.replace(' ', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
        for c in content:
            # Take care of duplicates (we're assuming that we're looking at the whole Math at once
            if c['id'] not in unique_content_ids:
                unique_content_ids.add(c['id'])
            else:
                continue

            if c['id'] not in listed_content_slugs and c['slug'] not in listed_content_slugs:
                eprint('Not listed: ' + c['slug'])
                continue

            # Bakalari fields
            dodavatel = 'Khan Academy'
            culture = '--'
            lang = {
                'audio': '--',
                'subtitles': '--',
                'text': 'CZ'
            }

            # Strip trailing newlines and occacional semicolons
            title = c['translated_title'].strip().replace(';',',')
            desc = c['translated_description'].strip().replace(';',',')

            out.write('%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (
                    c['id'], title, desc, c['ka_url'],
                    dodavatel, lang['audio'], lang['subtitles'], lang['text'], culture))

    print("Number of retrieved content items = ", len(unique_content_ids))

