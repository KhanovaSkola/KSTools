#!/usr/bin/env python3
from kapi import *
from utils import *

#YTID1='Pk4d9lY48GI'
#response = check_video(YTID1, kapi_headers)
#pprint(response)
#topic = "cc-early-math-add-sub-basics"
#tree = download_topic(topic)

download = True

if download:
    tree = download_topictree("Video")
    if tree != None:
        save_obj_text(tree, "topictree_txt")
        save_obj_bin(tree, "topictree_bin")
    else:
        tree = load_obj_bin("topictree_bin")
else:
    tree = load_obj_bin("topictree_bin")

videos = set()
tree_print_videoids(tree, videos)

# Get rid of duplicates
with open("allvideos_ids.dat","w") as out:
    for v in videos:
        out.write(v)

