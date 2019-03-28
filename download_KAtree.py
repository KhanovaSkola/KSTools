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
   parser.add_argument('-p','--print', dest='list', default=False, action="store_true", help='Only print topic names within given domain/subject/topic.')
   parser.add_argument('-l', '--lang', dest='lang', default = 'en', help='Language of the topic tree. (US by default)')
   return parser.parse_args()

# Currently, article type does not seem to work.
AVAILABLE_CONTENT_TYPES = ['video', 'article', 'exercise', 'topic', 'tutorial', 'all']

if __name__ == "__main__":

    opts = read_cmd()
    download = opts.download
    subject_title  = opts.subject
    what = opts.content
    lst = opts.list


    if what not in AVAILABLE_CONTENT_TYPES:
        print("ERROR: invalid content type argument:", opts.content)
        print("Possibilities are:", content_types)
        exit(1)

    if what == "tutorial" or what == "topic":
        download_type = 'video'
    else:
        download_type = what

    khan_tree = KhanContentTree(opts.lang, download_type)
    if download:
        kapi = KhanAPI(opts.lang)
        tree = kapi.download_topic_tree(download_type)
        if tree is not None:
            khan_tree.save(tree)
        else:
            print("ERROR: Could not download topic tree for locale " + opts.lang)
            sys.exit(1)
    else:
        tree = khan_tree.get()

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


    # Print unique videos to csv file by default
    if  what in ('video', 'exercise', 'all'):
        ids = set()
        data = []
        keys = ()
        if what == 'video' or what == 'all':
            keys = ('youtube_id', 'readable_id', 'duration')
        else:
            keys = ('slug', )

        khan_tree.get_unique_content_data(ids, data, keys, subtree)
 
        with open("unique_content.dat", "w") as f:
            for v in data:
                line = ''
                for k in keys:
                    line += "%s " % (v[k])
                line += '\n'
                f.write(line)

    
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

