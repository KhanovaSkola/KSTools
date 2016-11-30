#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time

#YTID1='Pk4d9lY48GI'
#response = kapi_check_video(YTID1)
#pprint(response)
#topic = "cc-early-math-add-sub-basics"
#tree = kapi_download_topic(topic)

# TODO: parse input from command line
def read_cmd():
   """Function for reading command line options."""
   desc = "Program for downloading and printing Khan Academy content tree." 
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-d','--download',dest='download',default=False,action="store_true", help='Download most up-to-date full tree?')
   parser.add_argument('-s','--subject', dest='subject', default=None, help='Print full tree for a given subject')
   parser.add_argument('-c','--content', dest='content', default="all", help='Which kind of content should we download? Options: Video|Exercise|Article|Topic')
   return parser.parse_args()

opts = read_cmd()
download = opts.download
subject  = opts.subject
what = opts.content
what = what.lower()

content_types = ["video", "article", "exercise", "topic","all"]

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
        tree = load_obj_bin("KAtree_"+what+"_bin")
else:
    tree = load_obj_bin("KAtree_"+what+"_bin")

if  what == 'video' or what == 'all':
    # We are using set to get rid of duplicates
    videos = set()

    kapi_tree_print_videoids(tree, videos)

    with open("allvideos_ids.dat","w") as out:
        for v in videos:
            out.write(v)



# Making large table of data for a given subject
if subject is not None:
    content = []

# Mapping KA tree to subjects
    subjects = {
        'science' : tree["children"][2],
        'biology' : tree["children"][2]['children'][0],
        'physics' : tree["children"][2]['children'][1],
        'chemistry' : tree["children"][2]['children'][2],
        'astronomy' : tree["children"][2]['children'][3],
        'medicine' : tree["children"][2]['children'][4],
        'electrical' : tree["children"][2]['children'][5],
        'organic_chemistry' : tree["children"][2]['children'][6],
        'math'  : tree["children"][1] # I think
    }

    if subject not in subjects:
        print("ERROR: I do not know subject ", subject)
        sys.exit(1)

    date = time.strftime("%d%m%Y")
    kapi_tree_print_full(subjects[subject], content)

    filename = what+"_"+subject+"_"+date+".txt"
    with open(filename,"w") as f:
        for c in content:
            f.write(c)



