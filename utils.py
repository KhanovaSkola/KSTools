#/usr/bin/env python3
import sys, os
import pickle
from pprint import pprint
from subprocess import Popen, PIPE
import string

def answer_me(question):
    print(question+" [yes/no]")
    while True:
        answer = input('-->')
        if answer.lower() == "yes":
            return True
        elif answer.lower() == "no":
            return False
        else:
            print("Please enter yes or no.")


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def epprint(*args, **kwargs):
    pprint(*args, stream=sys.stderr, **kwargs)

def save_obj_text(obj, name ):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, 0)

def save_obj_bin(obj, name ):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj_bin(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

def load_obj_text(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

# taken from: https://gist.github.com/seanh/93666
def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.
 
Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename."""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename


# Some usefull functions for manipulating Khan content tree

def print_children_titles(content_tree):
    if 'children' not in content_tree:
        return
    print("------------------------")
    print("Topic title | Topic slug")
    print("------------------------")
    for child in content_tree['children']:
       print("%s|%s" % (child['title'], child['slug']))

def print_dict_without_children(dictionary):
    for k in dictionary.keys():
        if k != 'children':
            print(k, dictionary[k])


def read_unique_data_from_one_column(fname):
    out = set()
    with open(fname, 'r') as f:
        for line in f:
            l = line.split()
            if len(l) != 1:
                print("ERROR during reading file ", listed_content_file)
                print("line: ", line)
                sys.exit(1)
            if len(l[0].strip()) == 0:
                print("ERROR: Empty line in file ", listed_content_file)
                sys.exit(1)
            out.add(l[0])
    return out

# We reuse this for EMA and Bakalari linking
# KA API returns also unlisted content, so we need to filter it out "manually"
def read_listed_content_slugs():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    LISTED_CONTENT_FILE = dir_path + '/indexable_slugs.txt'
    listed_content = read_unique_data_from_one_column(LISTED_CONTENT_FILE)
    return listed_content

def read_listed_topic_slugs():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    LISTED_TOPIC_FILE = dir_path + '/indexable_topic_slugs.txt'
    listed_topic_slugs = read_unique_data_from_one_column(LISTED_TOPIC_FILE)
    return listed_topic_slugs


def download_yt_subtitles(lang, sub_format, ytid, dirname = "subs"):
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid
    yt_download_cmd = 'youtube-dl --sub-lang %s --sub-format %s --write-sub \
    --skip-download --youtube-skip-dash-manifest %s' % (lang, sub_format, video_url)
    FNAME_OUT = "youtubedl.out"
    FNAME_ERR = "youtubedl.err"
    
    p = Popen(yt_download_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    with open(FNAME_OUT, 'a') as f:
        f.write(out.decode('UTF-8'))

    if err:
        with open(FNAME_ERR, 'a') as f:
            f.write(err.decode('UTF-8'))

    # youtubedl automatically download subs to file named after video title
    # Here we extract the name of the file and rename it to something more sane
    fname = out.decode('UTF-8').split('Writing video subtitles to: ')
    if len(fname) < 2:
        print("ERROR: Requested subtitles were not found on YouTube.")
        print("Look into file %s for more details" % FNAME_ERR)
        sys.exit(1)
        #return None

    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    fname = fname[1].rstrip();
    fname_target = "%s/%s.%s.%s" % (dirname, ytid, lang, sub_format)
    os.rename(fname, fname_target)
    print('Subtitles downloaded to file %s' % fname_target)

    with open(fname_target, 'r') as content_file:
        subs = content_file.read()

    return subs

