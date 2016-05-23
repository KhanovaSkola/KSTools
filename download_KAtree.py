#!/usr/bin/env python3
from kapi import *
from utils import *

#YTID1='Pk4d9lY48GI'
#response = check_video(YTID1, kapi_headers)
#pprint(response)
#topic = "cc-early-math-add-sub-basics"
#tree = download_topic(topic)

download = False
read = True

if download:
    tree = download_topictree("Video")
    save_obj_text(tree, "topictree_txt")
    save_obj_bin(tree, "topictree_bin")
elif read:
    tree = load_obj_bin("topictree_bin")

with open("allvideos_ids.dat", "rw") as f:
    yt = tree_print_videoids(tree, f)


