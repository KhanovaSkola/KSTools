#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for linking CS-Khan content for EMA reputation system."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Link given domain/subject.')
   parser.add_argument('-c','--content', dest='content', default='', help='Content kind: video|exercise|article|topic')
   return parser.parse_args()

# Currently, article type does not seem to work.
CONTENT_TYPES = ['video', 'article', 'exercise', 'topic']
LISTED_CONTENT_FILE = 'indexable_slugs.txt'
#TODO
SKIPPED_CONTENT_FILE = 'skipped_slugs.txt'

# TODO: Rename this function, re-use for skipped content
def read_listed_content_slugs(listed_content_file):
    listed_content = set()
    with open(listed_content_file, 'r') as f:
        for line in f:
            l = line.split()
            if len(l) != 1:
                print("ERROR during reading file " + listed_content_file)
                print("line: " + line)
            listed_content.add(l[0])

    return listed_content


if __name__ == '__main__':

    opts = read_cmd()
    topic_title  = opts.subject
    content_type = opts.content.lower()

    if content_type not in CONTENT_TYPES:
        print("ERROR: content argument: ", opts.content)
        print("Possibilities are: ", CONTENT_TYPES)
        exit(1)

    khan_tree = KhanContentTree('cs', content_type)
    tree = khan_tree.get()

    # Pick just concrete topic from KA tree
    if topic_title != 'root':
        subtree = find_ka_topic(tree, topic_title)
    else:
        subtree = tree

    if not subtree:
        print("ERROR: Could not find subtree for course: %s\n" % (topic_title))
        sys.exit(1)

    content = []
    ppuc_content = []
    unique_content_ids = set()
    # TODO: Filter out only given content type
    kapi_tree_get_content_items(subtree, content, content_type)
#    pprint(content[0].keys())
        
    # KA API returns unlisted content as well, need to deal with that externally
    listed_content = read_listed_content_slugs(LISTED_CONTENT_FILE)

    # TODO: Get rid of this and just use slugs everywhere
    #math_courses = ('early-math', 'arithmetic', 'basic-geo', 'trigonometry', 'algebra-basics', 'pre-algebra')
    #courses = math_courses
    #courses.append('music')
    #courses.append('mology-and-astronomy')
    #course = topic_title

    courses = {
        'early-math': 'early',
        'arithmetic': 'arith',
        'trigonometry': 'trig',
        'basic-geo': 'basicgeo',
        'pre-algebra': 'prealg',
        'algebra-basics': 'basicalg',
        'music': 'music',
        'cosmology-and-astronomy': 'astro'
    }

    course_subject_map = {
        'music': 'music',
        'astro': 'astro',
        'early': 'math',
        'arith': 'math',
        'basicgeo': 'math',
        'basicalg': 'math',
        'prealg': 'math',
        'trig': 'math'
    }

    try:
        course = courses[topic_title]
    except:
        eprint('ERROR: Invalid course! Valid course are:')
        eprint(courses)
        sys.exit(1)

    subject = course_subject_map[course]

    # Handle duplicities across courses
    # The ordering here is important!
    math_courses = ('early-math', 'arithmetic', 'basic-geo', 'trigonometry', 'algebra-basics', 'pre-algebra')
    # Go through all "preceding" math courses
    for crs in math_courses:
        if crs == topic_title:
            break
        subtree = find_ka_topic(tree, crs)
        temp_content = []
        kapi_tree_get_content_items(subtree, temp_content, content_type)
        for c in temp_content:
            unique_content_ids.add(c['id']) 

    if subject == 'math':
        print("Number of unique ids from preceding math courses = %d" % (len(unique_content_ids)))

    # TODO: Make ppuc_data keys same with json keys
    ppuc_data = {
        'lang': '5-cs',
         'source_type': '7-ANO', # OER
         'ct_types': {
            'video': '8-VI',
            'exercise': '8-IC',
            'article': '8-CL'
        },
        'licenses': {
            'cc-by-nc-nd': '1-CCBYNCND30',
            'cc-by-nc-sa': '1-CCBYNCSA30',
            'cc-by-sa': '1-CCBYSA30',
            'yt-standard': '1-OST'
        },
        'stupen': {
            'early': '2-Z',
            'arith': '2-Z',
            'prealg': '2-Z',
            'basicgeo': '2-Z',
            'basicalg': '2-Z',
            'trig': '2-G',
            'music': '2-NU',
            'astro': '2-NU'
        },
        'subjects': {
            'math': '9-03',
            'music': '9-11',
            'astro': '9-09' # TODO: 9-10' # Not clear whetherwe can have multiple types
        },
        'grades': {
            'early': '3-Z13',
            'arith': '',
            'prealg': '',
            'basicgeo': '',
            'basicalg': '',
            'trig': '3-SS',
            'music': '3-NU',
            'astro': '3-NU'
        },
        'gramotnost': {
            'math': '4-MA',
            'music': '4-NU',
            'astro': '4-PR'
        }
    }
    

    for v in content:

        if v['id'] not in listed_content and v['slug'] not in listed_content:
            eprint('Not listed: ' + v['slug'])
            continue

        if v['id'] in unique_content_ids:
            eprint("Found in previous math course, skipping: ", v['slug'])
            continue
        else:
            unique_content_ids.add(v['id'])

        try:
          item = {
            # Key items
            'id': v['id'],
            'url': v['ka_url'],
            'nazev': v['translated_title'],
            'popis': v['translated_description'],
            # Fixed items
            'autor': 'Khan Academy',
            'jazyk': ppuc_data['lang'],
            'dostupnost': ppuc_data['source_type'],
            # Optional fields
            # TODO: Creation date might not make sense...
            'datum_vzniku' : v['creation_date'],
            'vzdelavaci_obor': ppuc_data['subjects'][subject],
            'typ': ppuc_data['ct_types'][content_type],
            'stupen_vzdelavani': ppuc_data['stupen'][course],
            'gramotnost': ppuc_data['gramotnost'][subject]
            # KA API gives keywords in EN, commenting out for now....
#            'klicova_slova': v['keywords'],
#            'otevreny_zdroj': '7-ANO',
          }

          # Do not export empty fieds...TODO: should make this more general
          if course in ppuc_data['grades'].keys() and ppuc_data['grades'][course] != '':
              item['rocnik'] = ppuc_data['grades'][course]

          if 'ka_user_licence' in v.keys():
             item['licence'] = ppuc_data['licenses'][v['ka_user_license']]
          else:
             item['licence'] = ppuc_data['licenses']['cc-by-nc-sa'] # Let's just take the KA default

          if item['licence'] == '1-OST':
              if v['ka_user_licence'] == 'yt-standard':
                item['licence_url'] = 'https://www.youtube.com/static?template=terms&gl=CZ'
              else:
                eprint("WARNING: Missing license URL!")
                del item['licence']

          ppuc_content.append(item)

        except:
            eprint('Key error!')
            eprint(v)
            raise
 
    with open('ka_%s_%s.json' % (topic_title.replace(' ', '_').replace('-', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
        out.write(json.dumps(ppuc_content, ensure_ascii=False))

    print("Number of EMA content items in %s = %d" % (course, len(ppuc_content)))

