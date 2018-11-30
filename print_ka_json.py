#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for downloading and printing Khan Academy content tree."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-d','--download',dest='download',default=False, action='store_true', help='Download most up-to-date full tree?')
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Print full tree for a given domain/subject.')
   parser.add_argument('-c','--content', dest='content', default='', help='Which kind of content should we download? Options: video|exercise|article|topic')
   parser.add_argument('-l','--list', dest='list', default=False,action='store_true', help='Only list topic names within given domain/subject/topic.')
   return parser.parse_args()

# Currently, article type does not seem to work.
content_types = ['video', 'article', 'exercise', 'topic']
LISTED_CONTENT_FILE = 'indexable_slugs.txt'


def print_children_titles(content_tree):
    for child in content_tree['children']:
       pprint(child['title'])


def print_dict_without_children(dictionary):
    for k in dictionary.keys():
        if k != 'children':
            print(k, dictionary[k])

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
    download = opts.download
    topic_title  = opts.subject
    content_type = opts.content.lower()
    lst = opts.list

    if content_type not in content_types:
        print("ERROR: content argument: ", opts.content)
        print("Possibilities are: ", content_types)
        exit(1)

    if download:
        tree = kapi_download_topictree(content_type)
        if tree != None:
            #save_obj_text(tree, 'KAtree_'+what+'_txt')
            save_obj_bin(tree, 'KAtree_' + content_type + '_bin')
        else:
            tree = load_ka_tree(content_type)
    else:
        #tree = load_obj_bin('KAtree_'+what+'_bin')
        tree = load_ka_tree(content_type)

    # Pick just concrete topic from KA tree
    subtree = find_ka_topic(tree, topic_title)
    if not subtree:
        print("ERROR: Could not find subtree for course: %s\n" % (topic_title))
        # DH hack
        #subtree = tree
        sys.exit(1)

    content = []
    ppuc_content = []
    unique_content_ids = set()
    # TODO: Filter out only given content type
    kapi_tree_get_content_items(subtree, content, content_type)
#    pprint(content[0].keys())
        
    # KA API returns unlisted content as well, need to deal with that externally
    listed_content = read_listed_content_slugs(LISTED_CONTENT_FILE)

    courses = {
        'Early math': 'early',
        'Arithmetic': 'arith',
        'Trigonometry': 'trig',
        'Basic geometry': 'basicgeo',
        'Pre-algebra': 'prealg',
        'Algebra basics': 'basicalg',
        'Music': 'music',
        'Cosmology and astronomy': 'astro'
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
        print('Invalid course! Valid course are:')
        pprint(courses)
        raise

    subject = course_subject_map[course]

    # Handle duplicities across courses
    # The ordering here is important!
    math_courses = ('Early math', 'Arithmetic', 'Basic geometry', 'Trigonometry', 'Algebra basics', 'Pre-algebra')
    # Go through all "preceding" math courses
    for crs in math_courses:
        if crs == topic_title:
            break
        subtree = find_ka_topic(tree, crs)
        temp_content = []
        temp_content =  kapi_tree_get_content_items(subtree, temp_content, content_type)
        for c in temp_content:
            unique_content_ids.add(c['id']) 

    if subject == 'math':
        print("Number of unique ids from preceding math courses = %d" % (len(unique_content_ids)))

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
            'astro': '9-9' # TODO: 9-10' # Not clear whetherwe can have multiple types
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
            print('Not listed: ' + v['slug'])
            continue

        if v['id'] in unique_content_ids:
            print("Found in previous math course, skipping: ", v['slug'])
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
            'datum_vzniku' : v['creation_date'],
            'vzdelavaci_obor': ppuc_data['subjects'][subject],
            'typ': ppuc_data['ct_types'][content_type],
            'rocnik': ppuc_data['grades'][course],
            'stupen_vzdelavani': ppuc_data['stupen'][course],
            'gramotnost': ppuc_data['gramotnost'][subject]
            # KA API gives keywords in EN, commenting out for now....
#            'klicova_slova': v['keywords'],
#            'otevreny_zdroj': '7-ANO',
          }
          if 'ka_user_licence' in v.keys():
             item['licence'] = ppuc_data['licenses'][v['ka_user_license']]
          else:
             item['licence'] = ppuc_data['licenses']['cc-by-nc-sa'] # Let's just take the KA default

          if item['licence'] == '1-OST':
              if v['ka_user_licence'] == 'yt-standard':
                item['licence_url'] = 'https://www.youtube.com/static?template=terms&gl=CZ'
              else:
                print('Missing license URL!')
                del item['licence']

          ppuc_content.append(item)

        except:
            print('Key error!')
            pprint(v)
            raise
 
    with open('ka_%s_%s.json' % (topic_title.replace(' ', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
        out.write(json.dumps(ppuc_content, ensure_ascii=False))

    print("Number of PPUC content items = %d" % len(ppuc_content))
#    print("Number of unique ids = %d" % (len(unique_content_ids)))

    # Printing for Bakalari`
#    with open('ka_%s_%s.csv' % (topic_title.replace(' ', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
#        for c in content:
#            out.write('%s;%s;%s;%s\n' % (c['id'], c['youtube_id'], c['translated_youtube_id'],c['ka_url']))

#    pprint(ppuc_content[-1])

