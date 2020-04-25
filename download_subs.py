#!/usr/bin/env python3
from subprocess import Popen, PIPE, call, check_call
import argparse, sys, os
from utils import download_yt_subtitles

SUB_FORMAT = 'vtt'

def read_cmd():
   """Function for reading command line options."""
   parser = argparse.ArgumentParser()
   parser.add_argument('input_file', metavar='INPUT_FILE', help='Text file containing YouTube IDs and possibly filenames.')
   parser.add_argument('-l','--lang', dest='lang',required = True, help='Which language do we copy?')
   parser.add_argument('-d', '--dir', dest='dirname', required = True, help='Destination directory for subtitles')
   return parser.parse_args()

opts = read_cmd()
infile = opts.input_file

try:
    os.remove("youtubedl.out")
    os.remove("youtubedl.err")
except FileNotFoundError:
    pass

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(infile, "r") as f:
    for line in f:
        l = line.split()
        if len(l) > 0 and l[0][0] != "#":
            ytids.append(line.split())

if not os.path.isdir(opts.dirname):
    os.mkdir(opts.dirname)

# Main loop
for i in range(len(ytids)):
    ytid = ytids[i][0]
    subs = download_yt_subtitles(opts.lang, SUB_FORMAT, ytid, opts.dirname)

