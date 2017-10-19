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
content_types = ["video", "article", "exercise", "topic","all"]

def load_tree(content):
    if content not in content_types:
        return load_obj_bin("KAtree_"+content+"_bin")
    else:
        return load_obj_bin("KAtree_"+content+"_bin")
        print("Invalid content type!", content)
        print("Possibilities are:", content_types)
#        exit(0)

if __name__ == "__main__":

    opts = read_cmd()
    download = opts.download
    subject  = opts.subject
    what = opts.content.lower()
    lst = opts.list


    if what not in content_types:
        print("ERROR: content argument:", opts.content)
        print("Possibilities are:", content_types)
        sys.exit(1)

    if download:
        tree = kapi_download_topictree(what)
        if tree != None:
            save_obj_text(tree, "KAtree_"+what+"_txt")
            save_obj_bin(tree, "KAtree_"+what+"_bin")
        else:
            tree = load_tree(what)
    else:
        tree = load_obj_bin("KAtree_"+what+"_bin")

    if  what == 'video' or what == 'all':
        # We are using set to get rid of duplicates
        videos = set()
 
        kapi_tree_print_videoids(tree, videos)
 
        with open("allvideos_ids.dat","w") as out:
            for v in videos:
                out.write(v)

    if lst and subject == 'root':
        for child in tree["children"]:
            pprint(child['title'])
        exit(0)

    if subject == 'root':
        exit(0)

    # Mapping KA tree to subjects
    ind_math = 0
    ind_science = 1
    ind_chem = 5
    ind_org = 7
    ind_phys = 0
    ind_bio = 8
    ind_partner = 7
    ind_CC = 24

    try:
        subjects = {
        'science' : tree["children"][ind_science],
        'biology' : tree["children"][ind_science]['children'][ind_bio],
        'physics' : tree["children"][ind_science]['children'][ind_phys],
        'chemistry' : tree["children"][ind_science]['children'][ind_chem],
        'organic_chemistry' : tree["children"][ind_science]['children'][ind_org],
        'math'  : tree["children"][ind_math],
        'early_math'  : tree["children"][ind_math]["children"][5],
        'arithmetic' : tree["children"][ind_math]["children"][23],
        'partner' : tree["children"][ind_partner],
        'CC' : tree["children"][ind_partner]["children"][ind_CC],
        }
    except:
        print("Failed to locate subjects!")
        raise
    
    # Order of topics in Topic Tree often changes
    # The following is helpfull to determine where things are
    if lst:
        if subject not in subjects:
            for child in tree["children"]:
                pprint(child['title'])
        else:
            for child in subjects[subject]['children']:
                pprint(child['title'])
        exit(0)
    
    # Making large table of data for a given subject
    if subject is not None:
        content = []
    
    
        if subject not in subjects:
            print("ERROR: I do not know subject ", subject)
            sys.exit(1)
    
        date = time.strftime("%d%m%Y")
        kapi_tree_print_full(subjects[subject], content)

    filename = what+"_"+subject+"_"+date+".txt"
    with open(filename,"w") as f:
        for c in content:
            f.write(c)


