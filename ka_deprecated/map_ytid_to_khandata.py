#!/usr/bin/env python3
import kapi
import argparse, sys

def read_cmd():
   """Reading command line options."""
   desc = "Mapping YouTube IDs to data from Khan Topic Tree"
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE', help='Text file containing YouTube IDs in the first column.')
   parser.add_argument('-l','--lang',dest='lang', required = True, help='LTT locale')
   parser.add_argument('-a','--attribute',dest='key', help='Video attribute from Khan API (e.g. translated_youtube_id)')
   parser.add_argument('-p','--print', dest='list_keys', action = 'store_true',  help='Print available data attributes')
   parser.add_argument('-s','--skip-duplicates', dest='skip_duplicates', action = 'store_true',  help='Skip duplicate YouTube IDs')
   return parser.parse_args()

if __name__ == '__main__':

    opts = read_cmd()
    khan_api = kapi.KhanAPI(opts.lang)

    if opts.list_keys:
        example_ytid = 'ph64kEA6D4c'
        video = khan_api.download_video(example_ytid)
        for k in video.keys():
            print(k)
        sys.exit(0)

    if not opts.key:
        print("ERROR: You did not provide the attribute!")
        print("Try -h to get help.")
        sys.exit(1)

    unique_ytids = set()
    with open(opts.input_file, "r") as f:
        for line in f:
            l = line.split()
            # Skip empty and commented lines
            if len(l) > 0 and l[0] != '#':
                ytid = l[0]
            else:
                print()
                continue

            if ytid not in unique_ytids:
                unique_ytids.add(ytid)
            elif opts.skip_duplicates:
                continue

            # Try two times to get a response
            i = 0
            max_tries = 2
            video = None
            while not video and i < max_tries:
                video = khan_api.download_video(ytid)
                i += 1

            if video:
                a = video[opts.key].strip()
                print(ytid, a)
            else:
                print("Could not find video by YTID = ", ytid)

