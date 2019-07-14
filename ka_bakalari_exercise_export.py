#!/usr/bin/env python3
from kapi import *
import utils as u
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for relinking Khan Content Bakalari NEXT e-learning module."
   parser = argparse.ArgumentParser(description=desc)
#   parser.add_argument('-s','--subject', dest='subject', default='root', help='Relink content for a given domain/subject.')
#   parser.add_argument('-c','--content', dest='content', default='video', help='Which kind of content should we relink? Options: video')
   return parser.parse_args()

# TODO: All this should probably be moved into the bakalari_data dict
UNIT_TEST_TYPE = "web prezentace"
EXERCISE_TYPE = "web prezentace"
LESSON_TYPE = "web rozcestník"


# TODO: use ka_url or slugs instead of ids, which are unreliable
def read_linked_data():
    fname = 'khan_videos_linked_data.csv'
    delimiter = ';'
    linked_data = {}
    with open(fname, 'r') as f:
        for line in f:
            data = line.split(';')
            content_id = data[0]
            linked_data[content_id] = {
                    'grade': data[1],
                    'keywords': data[2]
                    }
    return linked_data


def fix_typos_in_keyword(keyword):
    fixed_keyword = keyword
    typo_map = {
            'násobění': 'násobení',
            'dělka': 'délka',
            'kracení': 'krácení',
            'ekvivlentní': 'ekvivalentní'
            }
    for typo in typo_map.keys():
        fixed_keyword = fixed_keyword.replace(typo, typo_map[typo])
    return fixed_keyword

def get_content_type(content):
    if content['kind'] == 'Exercise':
        return 'exercise'
    elif content['render_type'] == 'Topic':
        return 'unit_test'
    elif content['render_type'] == 'Tutorial':
        return 'lesson'
    else:
        print('ERROR: Unknown content type in')
        u.print_dict_without_children(content)
        sys.exit(1)

# TODO: Put related data to a separate structure from bakalari data
# and rename bakalari_data to BAKALARI_DATA
def print_bakalari_link(khan_data, bakalari_data, output_file):
    # TODO: Use this to automatically determine bakalari_data type and usage
    ct_type = get_content_type(khan_data)
    title = khan_data['translated_title'].strip().replace(';',',')
    desc = khan_data['translated_description'].strip().replace(';',',')
    # Write data from Khan API
    output_file.write('%s;%s;%s;%s;' % (
             khan_data['id'], title, desc, khan_data['ka_url']))
    # Bakalari fields
    output_file.write('%s;%s;%s;%s;%s;%s;%s;%s\n' % (
             bakalari_data['DODAVATEL'], bakalari_data['lang_audio'], bakalari_data['lang_subs'], bakalari_data['lang_text'],
             bakalari_data['CULTURE'], bakalari_data['keywords'], bakalari_data['grade'], bakalari_data['TYPE']))


def get_related_video_ids(ct_item):
    related_video_ids = []
    for v in c['related_content']:
        tmp = v.split(':')
        if tmp[0] == 'video' or tmp[0] == 'article':
            related_video_ids.append(tmp[1])
        elif len(tmp) == 1:
            related_video_ids.append(tmp[0])
        else:
            print('ERROR: Unexpected related_content value')
            print(v)
            print('For exercise titled:', c['title'])
            sys.exit(1)
    return related_video_ids

def get_related_data(ct_item, linked_data):
    related_video_ids = get_related_video_ids(ct_item)
    # TODO: we might need to switch to slugs instead of video_ids
    related_unique_keywords = set()
    related_grades = []
    for i in related_video_ids:
        if i in linked_data.keys():
            d = linked_data[i]
            related_grades.append(int(d['grade']))
            keywords = d['keywords'].split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                keyword = fix_typos_in_keyword(keyword)
                related_unique_keywords.add(keyword)

    related_grade = 0
    # Pick the highest related grade
    if len(related_grades) != 0:
        related_grades.sort(reverse=True)
        #related_grade = str(related_grades[0])
        related_grade = related_grades[0]
        if related_grades[0] != related_grades[-1]:
            eprint('WARNING: Incompatible related grades for exercise ', c['slug'])
            eprint('Video IDS:', related_video_ids)
            eprint('Lowest and highest grade:', related_grades[-1], related_grades[0])
            eprint('Grade difference:', related_grades[0] - related_grades[-1])

    return related_unique_keywords, related_grade


def stringify_keywords(keyword_set):
    keywords = ''
    for k in keyword_set:
        keywords += k + ','
    keywords = keywords.rstrip(',')
    return keywords

def stringify_grade(grade):
    if grade < 0:
        print("ERROR: Grade cannot be < 0")
    elif grade == 0:
        return ''
    else:
        return str(grade)

def update_bakalari_data(bak_data, ct_type, keywords, grade):
    bak_data['TYPE'] = ct_type
    bak_data['keywords'] = keywords
    bak_data['grade'] = grade

def get_unit_test_link(unit):
    unit_url = unit['ka_url']
    unit_slug = unit['slug']
    unit_test_url = "%s/test/%s-unit-test?modal=1" % (unit_url, unit_slug)
    return unit_test_url

def get_unit_test_title(unit):
    return "Souhrný test ke kapitole: " + unit['translated_title']

def get_unit_test_description(unit):
    # TODO: What should the description be?
    # return "Obsahuje příklady z lekcí: " + get_lesson_titles(unit)
    return unit['translated_description']

# Filter out unlisted content
def get_listed_content(content, listed_content_slugs):
    listed_content = []
    # This is weird, cause our listed_content_file contains either slug or id
    # for historical reasons (this is what we got from a custom export by KAHQ)
    for c in content:
        if c['id'] in listed_content_slugs or c['slug'] in listed_content_slugs:
            listed_content.append(c)
    return listed_content

# Filter out duplicate content
def get_unique_content(content, unique_content_ids):
    unique_content = []
    for c in content:
        if c['id'] not in unique_content_ids:
            unique_content.append(c)
            unique_content_ids.add(c['id'])
    return unique_content

CONTENT_TYPES = ['exercise']

if __name__ == '__main__':

    opts = read_cmd()
#    topic_title  = opts.subject
#    content_type = opts.content.lower()
    # Let's just do Math for now
    topic_title = 'math'
    content_type = 'exercise'

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

    # KA API returns unlisted content as well, need to deal with that externally
    listed_content_slugs = u.read_listed_content_slugs()
    listed_topic_slugs = u.read_listed_topic_slugs()
    # External data from Bakalari linkers
    khan_video_linked_data = read_linked_data()

    # Bakalari fields
    bakalari_data = {
        'DODAVATEL': 'Khan Academy',
        'CULTURE': '--',
        'lang_audio': '--',
        'lang_subs': '--',
        'lang_text': 'CZ',
        'TYPE': '',
        'USAGE': {
            'unit_test': 'online test',
            'exercise': 'cvičení (příklad)',
            'lesson': 'výklad látky, test online, cvičení (příklad)'
            },
        # The following are variables
        'keywords': '',
        'grade': ''
    }

    linked_data = {
        'keywords': '',
        'grade': ''
            }

    OUTPUT_FNAME = 'bakalari_khan_export_%s_%s.csv' % (topic_title.replace(' ', '_').lower(), content_type)
    f = open(OUTPUT_FNAME, 'w')

    unique_content_ids = set()
    units = []
    lesson_keywords = set()
    unit_keywords = set()

    khan_tree.get_units(units, subtree)

    for unit in units:
        if unit['slug'] not in listed_topic_slugs:
            continue
        lessons = []
        unit_keywords.clear()
        unit_grade = 0

        khan_tree.get_lessons(lessons, unit)

        # TODO: Skip unlisted lessons, but hopefully not necessary
        for lesson in lessons:
            content = []
            lesson_keywords.clear()
            lesson_grade = 0

            kapi_tree_get_content_items(lesson, content, content_type)

            # Filter out unlisted content first
            listed_content = get_listed_content(content, listed_content_slugs)

            # Maybe turn this for loop into get_lesson_linked_data
            # Listed content can contain duplicities from previous lessons,
            # but that is okay because we want the linked data from them!
            for c in listed_content:
                keywords, grade = get_related_data(c, khan_video_linked_data)
                # Union of sets
                lesson_keywords.update(keywords)
                if grade > lesson_grade:
                    lesson_grade = grade

            # Filter out duplicities now!
            unique_content = get_unique_content(listed_content, unique_content_ids)

            # Print lesson link if the lesson is not empty
            # If lessons contains only duplicates, we do not print it
            if len(unique_content) > 0:
                keyword_string = stringify_keywords(lesson_keywords)
                grade_string = stringify_grade(lesson_grade)
                update_bakalari_data(bakalari_data, LESSON_TYPE, keyword_string, grade_string)
                print_bakalari_link(lesson, bakalari_data, f)

            # Print links for individual content items
            for c in unique_content:
                keywords, grade = get_related_data(c, khan_video_linked_data)
                keyword_string = stringify_keywords(keywords)
                grade_string = stringify_grade(grade)
                update_bakalari_data(bakalari_data, EXERCISE_TYPE, keyword_string, grade_string)
                print_bakalari_link(c, bakalari_data, f)

            unit_keywords.update(lesson_keywords)
            if lesson_grade > unit_grade:
                unit_grade = lesson_grade

        # Print UNIT TEST
        keyword_string = stringify_keywords(unit_keywords)
        grade_string = stringify_grade(unit_grade)
        update_bakalari_data(bakalari_data, UNIT_TEST_TYPE, keyword_string, grade_string)
        # A dirty hack, we want to link to a Unit TEST, not the Unit itself
        unit['ka_url'] = get_unit_test_link(unit)
        unit['translated_title'] = get_unit_test_title(unit)
        unit['translated_description'] = get_unit_test_description(unit)
        print_bakalari_link(unit, bakalari_data, f)

    f.close()
    print("Number of retrieved content items = ", len(unique_content_ids))
