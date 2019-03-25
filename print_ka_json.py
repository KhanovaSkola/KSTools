#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for linking Khan content for PPUC reputation system."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Print full tree for a given domain/subject.')
   parser.add_argument('-c','--content', dest='content', default='', help='Which kind of content should we download? Options: video|exercise|article|topic')
   parser.add_argument('-l','--list', dest='list', default=False, action='store_true', help='Only list topic names within given domain/subject/topic.')
   parser.add_argument('-b','--bakalari', dest='bakalari', default=False, action='store_true', help='Print info for Bakalari linking.')
   return parser.parse_args()

# Currently, article type does not seem to work.
CONTENT_TYPES = ['video', 'article', 'exercise', 'topic']
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
    topic_title  = opts.subject
    content_type = opts.content.lower()
    lst = opts.list

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
        print(subtree)
        sys.exit(1)

    content = []
    ppuc_content = []
    unique_content_ids = set()
    # TODO: Filter out only given content type
    kapi_tree_get_content_items(subtree, content, content_type)
#    pprint(content[0].keys())
        
    # KA API returns unlisted content as well, need to deal with that externally
    listed_content = read_listed_content_slugs(LISTED_CONTENT_FILE)

    # Printing for Bakalari`
    if opts.bakalari:
        ksid_ytid_map_file = 'ka_indexable_ytid_ksid_map.dat'
        unique_content_ids = set()
        ytid_ksid_map = {}
        ytid_on_ks = set()
        with open(ksid_ytid_map_file, 'r') as f:
            for line in f:
                l = line.split()
                if len(l) < 2 and len(l) > 3:
                    print("Fatal error in reading file;", ksid_ytid_map_file)
                ksid = l[0]
                ytid = l[1]
                ytid_ksid_map[ytid] = ksid
                if len(l) == 3:
                    ytid_original = l[2]
                    ytid_ksid_map[ytid_original] = ksid
                ytid_on_ks.add(ytid)


        ka = KhanAPI('cs')
        with open('bakalari_relinking_%s_%s.csv' % (topic_title.replace(' ', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
            for c in content:
                # Take care of duplicates (we're assuming that we're looking at the whole Math at once
                if c['id'] not in unique_content_ids:
                    unique_content_ids.add(c['id'])
                else:
                    continue

                # Bakalari fields
                dodavatel = 'Khan Academy'
                culture = '--'
                lang = {
                    'audio': 'CZ',
                    'subtitles': '--',
                    'text': 'CZ'
                }

                ytid = c['youtube_id']
                translated_ytid = c['translated_youtube_id']
                vid = c
                # Here we workaround a bug in API which sometimes seems to return wrong youtube_id
                if c['youtube_id'] == c['translated_youtube_id']:
                    vid = ka.download_video(c['readable_id'])
                    if vid:
                        ytid = vid['youtube_id']
                    else:
                        print(c)
                        print("ERROR: Could not find video, ytid = ", ytid)
                        sys.exit(1)
                    #print(c)

                # Subtitled video, modify fields accordingly
                # Unfortunatelly, we cannot properly detect dubbed videos for now...
                if vid['youtube_id'] == vid['translated_youtube_id']:
                    lang = {
                        'audio': 'EN',
                        'subtitles': 'CS',
                        'text': 'EN'
                    }

                # Strip newlines (not tested) and occacional semicolons
                vid['translated_title'].replace('\n','').replace(';',',')
                vid['translated_description'].replace('\n','').replace(';',',')

                if ytid in ytid_ksid_map.keys():
                    out.write('%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (ytid_ksid_map[ytid],
                        vid['id'], vid['translated_title'], vid['translated_description'], vid['ka_url'],
                        dodavatel, lang['audio'], lang['subtitles'], lang['text'], culture))
                elif translated_ytid in ytid_ksid_map.keys():
                    out.write('%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % (ytid_ksid_map[translated_ytid],
                        vid['id'], vid['translated_title'], vid['translated_description'], vid['ka_url'],
                        dodavatel, lang['audio'], lang['subtitles'], lang['text'], culture))

        print("Number of retrieved content items = ", len(unique_content_ids))
        print("Number of videos on Khanova skola = ", len(ytid_on_ks))
        sys.exit(0)


    # Printing for PPUC reputation site
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
        kapi_tree_get_content_items(subtree, temp_content, content_type)
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


#    pprint(content[-1])

