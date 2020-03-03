#!/usr/bin/env python3
import kapi
import argparse, sys

def read_cmd():
   """Reading command line options."""
   desc = "Mapping video data from Khan Topic Tree"
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file', metavar='INPUT_FILE', help='Text file containing input attributes (YouTube IDs, slugs etc.), one per line.')
   parser.add_argument('-l','--lang',dest='lang', required = True, help='LTT locale')
   parser.add_argument('-c','--content-type',dest='content_type', required = True, help='video|exercise|article')
   parser.add_argument('-o','--output-attribute',dest='output_key', help='Video attribute from Khan API (e.g. translated_youtube_id)')
   parser.add_argument('-i','--input-attribute',dest='input_key', help='Video attribute from Khan API (e.g. translated_youtube_id)')
   parser.add_argument('-p','--print', dest='list_keys', action = 'store_true',  help='Print available data attributes')
   return parser.parse_args()

if __name__ == '__main__':

    opts = read_cmd()
    #khan_api = kapi.KhanAPI(opts.lang)
    khan_tree = kapi.KhanContentTree(opts.lang, opts.content_type)

    if opts.list_keys:
        example_ytid = 'ph64kEA6D4c'
        video = khan_api.download_video(example_ytid)
        for k in video.keys():
            print(k)
        sys.exit(0)

    if not opts.output_key:
        print("ERROR: You did not provide the output attribute!")
        print("Try -h to get help.")
        sys.exit(1)

    if not opts.input_key:
        print("ERROR: You did not provide the output attribute!")
        print("Try -h to get help.")
        sys.exit(1)

    with open(opts.input_file, "r") as f:
        for line in f:
            l = line.split()
            # Skip empty and commented lines
            if len(l) > 0 and l[0] != '#':
                inp = l[0]
            else:
                continue

            # TODO: Only call API directly for specific atrribute like
            # translated_* etc
            # Try two times to get a response
            """
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
            """
            v = khan_tree.find_video(inp, opts.input_key)
            if v is not None:
                print(v[opts.output_key])
            else:
                print("NOT FOUND")


