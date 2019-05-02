#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time


def read_cmd():
   """Function for reading command line options."""
   desc = "Program for printing Khan Academy content tree into CSV file." 
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Print full tree for a given domain/subject.')
   parser.add_argument('-c','--content', dest='content_type', required = True, help='Which kind of content should we download? Options: video|exercise|article|topic')
   parser.add_argument('-p','--print', dest='list', default=False, action="store_true", help='Only list topic names within given domain/subject/topic.')
   parser.add_argument('-l', '--lang', dest='lang', default = 'en', help='Language of the topic tree. (US by default)')
   return parser.parse_args()

# Currently, article type does not seem to work.
AVAILABLE_CONTENT_TYPES = ['video', 'article', 'exercise', 'topic', 'tutorial']

if __name__ == "__main__":

    opts = read_cmd()
    subject_title  = opts.subject
    lst = opts.list


    if opts.content_type not in AVAILABLE_CONTENT_TYPES:
        print("ERROR: invalid content type argument:", opts.content_type)
        print("Possibilities are:", content_types)
        exit(1)

    if opts.content_type == "tutorial" or opts.content_type == "topic":
        download_type = 'video'
    else:
        download_type = opts.content_type

    khan_tree = KhanContentTree(opts.lang, download_type)
    tree = khan_tree.get()

    if subject_title == 'root':
        subtree = tree
    else:
        subtree = find_ka_topic(tree, subject_title)

    # The following is helpful to determine where things are
    if lst:
        if subtree is not None:
            #print("Printing dictionary for topic ", subject_title)
            #print_dict_without_children(subtree)
            #print("=============================")
            print("Listing topic children for %s" % (subject_title))
            print_children_titles(subtree)
            sys.exit(0)
        else:
            print("ERROR: Could not find topic titled: "+subject_title)
            sys.exit(1)


    # Print unique videos to csv file by default
    if  opts.content_type in ('video', 'exercise', 'all'):
        ids = set()
        data = []
        keys = ()
        if opts.content_type == 'video' or opts.content_type == 'all':
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
    
    if opts.content_type == 'tutorial':
        kapi_tree_print_tutorials(subtree, content)
    else:
        kapi_tree_print_full(subtree, content)

    filename = opts.content_type + "_" + format_filename(subject_title) + "_" + date + ".csv"
    with open(filename, "w", encoding = 'utf-8') as f:
        for c in content:
            f.write(c)

