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
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Relink content for a given domain/subject.')
   parser.add_argument('-c','--content', dest='content', default='video', help='Which kind of content should we relink? Options: video')
   return parser.parse_args()

CONTENT_TYPES = ['video']
KSID_YTID_MAP_FILE = 'ka_indexable_ytid_ksid_map.dat'

if __name__ == '__main__':

    opts = read_cmd()
    topic_title  = opts.subject
    content_type = opts.content.lower()

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
    ytid_ksid_map = {}
    ytid_on_ks = set()

    # TODO: Make this into function
    with open(KSID_YTID_MAP_FILE, 'r') as f:
        for line in f:
            l = line.split()
            if len(l) < 2 and len(l) > 3:
                print("Fatal error in reading file;", KSID_YTID_MAP_FILE)
                sys.exit(1)
            ksid = l[0]
            ytid = l[1]
            ytid_ksid_map[ytid] = ksid
            if len(l) == 3:
                ytid_original = l[2]
                ytid_ksid_map[ytid_original] = ksid
            ytid_on_ks.add(ytid)


    ka = KhanAPI('cs')
    with open('bakalari_relinking_%s_%s.csv' % (topic_title.replace(' ', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
        for c in content:
            # Take care of duplicates (we're assuming that we're looking at the whole Math at once
            if c['id'] not in unique_content_ids:
                unique_content_ids.add(c['id'])
            else:
                continue

            # Bakalari fields
            dodavatel = 'Khan Academy'
            culture = '--'
            lang = {
                'audio': 'CZ',
                'subtitles': '--',
                'text': 'CZ'
            }

            ytid = c['youtube_id']
            translated_ytid = c['translated_youtube_id']
            vid = c
            # Here we workaround a bug in API which sometimes seems to return wrong youtube_id
            if c['youtube_id'] == c['translated_youtube_id']:
                vid = ka.download_video(c['readable_id'])
                if vid:
                    ytid = vid['youtube_id']
                else:
                    print(c)
                    print("ERROR: Could not find video, ytid = ", ytid)
                    sys.exit(1)
                #print(c)

            # Subtitled video, modify fields accordingly
            if vid['youtube_id'] == vid['translated_youtube_id']:
                lang = {
                    'audio': 'EN',
                    'subtitles': 'CS',
                    'text': 'EN'
                }

            # Strip newlines (not tested) and occacional semicolons
            vid['translated_title'].replace('\n','').replace(';',',')
            vid['translated_description'].replace('\n','').replace(';',',')

            if ytid in ytid_ksid_map.keys():
                out.write('%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (ytid_ksid_map[ytid],
                    vid['id'], vid['translated_title'], vid['translated_description'], vid['ka_url'],
                    dodavatel, lang['audio'], lang['subtitles'], lang['text'], culture))
            elif translated_ytid in ytid_ksid_map.keys():
                out.write('%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (ytid_ksid_map[translated_ytid],
                    vid['id'], vid['translated_title'], vid['translated_description'], vid['ka_url'],
                    dodavatel, lang['audio'], lang['subtitles'], lang['text'], culture))

    print("Number of retrieved content items = ", len(unique_content_ids))
    print("Number of videos on Khanova skola = ", len(ytid_on_ks))

