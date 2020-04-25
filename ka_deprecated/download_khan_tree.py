#!/usr/bin/env python3
import kapi
import argparse, sys

def read_cmd():
   """Function for reading command line options."""
   desc = "Script for downloading Khan Academy content tree." 
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-c','--content', dest='content_type', required = True, help='Which kind of content should we download? Options: video|exercise|article|topic')
   parser.add_argument('-l', '--lang', dest='lang', default = 'en', help='Language of the topic tree. (US by default)')
   return parser.parse_args()

# Currently, article type does not work
# Each article need to be downloaded separately via kapi.download_article(article_id)
AVAILABLE_CONTENT_TYPES = ['video', 'exercise', 'topic']

if __name__ == "__main__":

    opts = read_cmd()

    if opts.content_type not in AVAILABLE_CONTENT_TYPES:
        print("ERROR: invalid content type argument:", opts.content_type)
        print("Available:", AVAILABLE_CONTENT_TYPES)
        exit(1)

    khan_tree = kapi.KhanContentTree(opts.lang, opts.content_type)
    khan_api = kapi.KhanAPI(opts.lang)
    tree = khan_api.download_topic_tree(opts.content_type)
    if tree is not None:
        khan_tree.save(tree)
        print("Successfully downloaded Khan %s topic tree for locale %s" % (opts.content_type, opts.lang))
    else:
        print("ERROR: Could not download topic tree for locale " + opts.lang)
        sys.exit(1)

