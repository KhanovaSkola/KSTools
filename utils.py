import sys
import pickle

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

