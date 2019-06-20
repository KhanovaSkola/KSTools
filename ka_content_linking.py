#!/usr/bin/env python3
from kapi import *
import utils
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for linking CS-Khan content for EMA reputation system."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-s','--subject', dest='subject', default = 'root', help = 'Link given course.')
   parser.add_argument('-c','--content', dest='content', required = True, help = 'Content kind: video|exercise')
   parser.add_argument('-a','--all', dest = 'all', action = 'store_true', help = 'Print all available courses')
   # TODO: Add verbose parameter
   return parser.parse_args()

# Currently, article type does not seem to work.
CONTENT_TYPES = ['video', 'exercise']
#TODO
SKIPPED_CONTENT_FILE = 'skipped_slugs.txt'

EMA_OPTIONAL_DATA = {
    # TODO: What about subtitles videos?
    'jazyk': '5-cs',
    'autor': 'Khan Academy',
    'dostupnost': '7-ANO', # OER
    'typ': {
        'video': '8-VI',
        'exercise': '8-IC',
        'article': '8-CL'
    },
    'licence': {
        'cc-by-nc-nd': '1-CCBYNCND30',
        'cc-by-nc-sa': '1-CCBYNCSA30',
        'cc-by-sa': '1-CCBYSA30',
        'yt-standard': '1-OST'
    },
    'stupen_vzdelavani': {
        'early-math': '2-Z',
        'arithmetic': '2-Z',
        'pre-algebra': '2-Z',
        'basic-geo': '2-Z',
        'algebra-basics': '2-Z',
        'trigonometry': '2-G',
        'music': '2-NU',
        'cosmology-and-astronomy': '2-NU'
    },
    'vzdelavaci_obor': {
        'math': '9-03',
        'music': '9-11',
        'astro': '9-09' # TODO: 9-10' # Not clear whether we can have multiple types
    },
    'rocnik': {
        'early-math': '3-Z13',
        'trigonometry': '3-SS',
    },
    'gramotnost': {
        'math': '4-MA',
        'music': '4-NU',
        'astro': '4-PR'
    }
}

def ema_print_course_content(course, content, content_type):
    ema_content = []
    unique_content_ids = set()

    # KA API returns unlisted content as well, need to deal with that externally
    listed_content = utils.read_listed_content_slugs()

    course_subject_map = {
        'music': 'music',
        'cosmology-and-astronomy': 'astro',
        'early-math': 'math',
        'arithmetic': 'math',
        'basic-geo': 'math',
        'algebra-basics': 'math',
        'pre-algebra': 'math',
        'trigonometry': 'math'
    }

    subject = course_subject_map[course]

    # Go through all "preceding" math courses
    # TODO: Handle duplicities accross all domains
    for crs in math_courses:
        if crs == course:
            break
        subtree = find_ka_topic(tree, crs)
        temp_content = []
        kapi_tree_get_content_items(subtree, temp_content, content_type)
        for c in temp_content:
            unique_content_ids.add(c['id']) 

    if subject == 'math':
        print("Number of unique ids from preceding math courses = %d" % (len(unique_content_ids)))

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
            'autor': EMA_OPTIONAL_DATA['autor'],
            'jazyk': EMA_OPTIONAL_DATA['jazyk'],
            'dostupnost': EMA_OPTIONAL_DATA['dostupnost'],
            # Optional fields
            'typ': EMA_OPTIONAL_DATA['typ'][content_type],
            'stupen_vzdelavani': EMA_OPTIONAL_DATA['stupen_vzdelavani'][course],
            'vzdelavaci_obor': EMA_OPTIONAL_DATA['vzdelavaci_obor'][subject],
            'gramotnost': EMA_OPTIONAL_DATA['gramotnost'][subject],
            # TODO: Creation date might not make sense...
            'datum_vzniku': v['creation_date']
            # KA API gives keywords in EN, commenting out for now....
#            'klicova_slova': v['keywords'],
#            'otevreny_zdroj': '7-ANO',
          }

          # Do not export empty fieds...
          # TODO: should make this more general
          if course in EMA_OPTIONAL_DATA['rocnik'].keys() and EMA_OPTIONAL_DATA['rocnik'][course] != '':
              item['rocnik'] = EMA_OPTIONAL_DATA['rocnik'][course]

          # TODO: Refactor this, it is confusing
          if 'ka_user_licence' in v.keys():
             item['licence'] = EMA_OPTIONAL_DATA['licence'][v['ka_user_license']]
          else:
             item['licence'] = EMA_OPTIONAL_DATA['licence']['cc-by-nc-sa'] # Let's just take the KA default

          if item['licence'] == '1-OST':
              if v['ka_user_licence'] == 'yt-standard':
                item['licence_url'] = 'https://www.youtube.com/static?template=terms&gl=CZ'
              else:
                eprint("WARNING: Missing license URL!")
                del item['licence']

          ema_content.append(item)

        except:
            eprint('Key error!')
            eprint(v)
            raise
 
    with open('ka_%s_%s.json' % (course.replace('-', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
        out.write(json.dumps(ema_content, ensure_ascii=False))

    print("Number of EMA %s in %s = %d" % (content_type, course, len(ema_content)))


if __name__ == '__main__':

    opts = read_cmd()
    course = opts.subject
    content_type = opts.content.lower()

    if content_type not in CONTENT_TYPES:
        print("ERROR: content argument: ", opts.content)
        print("Possibilities are: ", CONTENT_TYPES)
        exit(1)

    # Handle duplicities across courses
    # The ordering here is important!
    math_courses = ['early-math', 'arithmetic', 'basic-geo', 'trigonometry', 'algebra-basics', 'pre-algebra']
    available_courses = math_courses
    available_courses.append('music')
    available_courses.append('cosmology-and-astronomy')

    if opts.all:
        courses = available_courses
    else:
        courses = [course]
        if course not in available_courses:
            eprint('ERROR: Invalid course! Valid course are:')
            eprint(courses)
            sys.exit(1)

    khan_tree = KhanContentTree('cs', content_type)
    tree = khan_tree.get()

    for c in courses:
        subtree = find_ka_topic(tree, c)
        if not subtree:
            print("ERROR: Could not find subtree for course: %s\n" % (c))
            sys.exit(1)

        content = []
        kapi_tree_get_content_items(subtree, content, content_type)
        
        ema_print_course_content(c, content, content_type)

