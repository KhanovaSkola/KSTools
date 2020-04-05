#!/usr/bin/env python3
from subprocess import Popen, PIPE, call, check_call
import argparse, sys, os

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

def download_yt_subtitles(lang, SUB_FORMAT, dirname, ytid):
    video_url = "https://www.youtube.com/watch?v=%s" % ytid
    ytdownload = "youtube-dl --sub-lang %s --sub-format %s --write-sub --skip-download %s" %\
                 (lang,  SUB_FORMAT, video_url)
    
    p = Popen(ytdownload, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    f = open("youtubedl.out", "a")
    f.write(out.decode('UTF-8'))
    f.close()
    if err:
        f = open("youtubedl.err", "a")
        f.write(err.decode('UTF-8'))
        f.close()

    fname = out.decode('UTF-8').split('Writing video subtitles to: ')
    if len(fname) < 2:
       print("ERROR: Requested subtitles were not found on YouTube.")
       f = open("failed_yt.dat", "a")
       f.write(ytid_from+'\n')
       f.close()
       return False

    fname = fname[1].rstrip();
    fname_target = "%s/%s.%s.%s" % (dirname, ytid, lang, SUB_FORMAT)
    os.rename(fname, fname_target)
    print('Subtitles downloaded to file %s' % fname_target)
    return True


# Main loop
for i in range(len(ytids)):
    ytid = ytids[i][0]

    subs = False
    if not os.path.isdir(opts.dirname):
        os.mkdir(opts.dirname)
    subs = download_yt_subtitles(opts.lang, SUB_FORMAT, opts.dirname, ytid)

