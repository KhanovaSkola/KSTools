#!/usr/bin/env python3
import kapi
import argparse, sys

def read_cmd():
   """Reading command line options."""
   desc = "Mapping YouTube IDs to data from Khan Topic Tree"
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE', help='.tsv file, columns: Domain,Course,Unit,Tutorial,YouTube ID.')
   parser.add_argument('-l','--lang',dest='lang', required = True, help='LTT locale')
#   parser.add_argument('-a','--attribute',dest='key', help='Video attribute from Khan API (e.g. translated_youtube_id)')
   return parser.parse_args()

if __name__ == '__main__':

    opts = read_cmd()
    #opts.key = 'translated_title'

    khan_api = kapi.KhanAPI(opts.lang)
    tree_api = kapi.KhanContentTree(opts.lang, 'video')

    topics = []
    topic_title_map = {}
    tree_api.get_topics(topics)
    for topic in topics:
        english_title = topic['title'].strip().lower()
        translated_title = topic['translated_title'].strip().lower()
        topic_title_map[english_title] = translated_title

    with open(opts.input_file, "r") as f:
        for line in f:
            l = line.split("\t")
            titles = {}
            # Skip empty and commented lines
            if len(l) > 0 and l[0] != '#':
                titles['domain'] = l[0].strip().lower()
                titles['course'] = l[1].strip().lower()
                titles['unit'] = l[2].strip().lower()
                titles['lesson'] = l[3].strip().lower()
                ytid = l[4].strip()
            else:
                print()
                continue

            translated_titles = {}
            for key in titles.keys():
                try:
                    translated_titles[key] = topic_title_map[titles[key]]
                except KeyError:
                    translated_titles[key] = titles[key]

            # Try two times to get a response
            i = 0
            max_tries = 2
            video = None
            while not video and i < max_tries:
                video = khan_api.download_video(ytid)
                i += 1

            if video:
                translated_video_title = video['translated_title'].strip()
                print("%s\t%s\t%s\t%s\t%s" % 
                        (translated_titles['domain'], translated_titles['course'],
                        translated_titles['unit'], translated_titles['lesson'],
                        translated_video_title))
            else:
                print("Could not find video by YTID = ", ytid)

