import sys
import pickle
from pprint import pprint
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
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, 0)

def save_obj_bin(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj_bin(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def load_obj_text(name ):
    with open(name + '.pkl', 'rb') as f:
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


