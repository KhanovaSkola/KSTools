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
   parser.add_argument('-d','--debug', dest='debug', default = False, action = 'store_true', help='Print debug info.')
#   parser.add_argument('-s','--subject', dest='subject', default='root', help='Relink content for a given domain/subject.')
#   parser.add_argument('-c','--content', dest='content', default='video', help='Which kind of content should we relink? Options: video')
   return parser.parse_args()


"""Bakalari fields constants"""
BAKALARI_DATA = {
    'DODAVATEL': 'Khan Academy',
    'CULTURE': '--',
    'lang_audio': '--',
    'lang_subs': '--',
    'lang_text': 'CZ',
    'TYPE': {
        'unit_test': "web prezentace",
        'exercise': "web prezentace",
        'lesson': "web rozcestník"
        },
    'USAGE': {
        'unit_test': 'test online',
        'exercise': 'cvičení (příklad)',
        'lesson': 'výklad látky, cvičení (příklad)'
        },
    'SUBJECT': 'M',
    'AUTHOR': 'DH',
    'ACCESS': 'Zdarma'
}

def read_linked_data():
    """
    Read related data from linked videos
    | ID | studyYear | Relevance | Level | Klíč. slova
    """
    fname = 'khan_videos_linked_data.tsv'
    delimiter = '\t'
    linked_data = {}
    with open(fname, 'r') as f:
        for line in f:
            data = line.split(delimiter)
            content_id = data[0]
            linked_data[content_id] = {
                'grade': data[1],
                'relevance': data[2],
                'difficulty': data[3],
                'keywords': data[4]
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
        utils.print_dict_without_children(content)
        sys.exit(1)


def print_header(output_file):
    output_file.write("originalId;title;description;link;")
    output_file.write("Keywords;studyYear;Relevance;Level;")
    output_file.write("Předmět;Jazyk-mluvené slovo;Jazyk-titulky;Jazyk - texty;")
    output_file.write("Kulturně závislý obsah;Typ materiálu;Způsob využití;")
    output_file.write("Dodavatel;Přístup;Autor\n")

def print_bakalari_link(khan_data, related_data, bakalari_data, output_file):
    ct_type = get_content_type(khan_data)
    print_khan_data(khan_data, output_file)
    print_related_data(related_data, output_file)
    print_bakalari_data(bakalari_data, ct_type, output_file)
    output_file.write('\n')

def print_related_data(related_data, output_file):
    """
    Write related data from linked videos
    | Klíč. slova | studyYear| Relevance | Level |
    """
    keywords = stringify_keywords(related_data['keywords'])
    grade = stringify_number(related_data['grade'])

    # Sometimes relevance contains bad data, not sure how it got there:
    if related_data['relevance'] == -1:
        related_data['relevance'] = 3
    relevance = stringify_number(related_data['relevance'])
    difficulty = stringify_number(related_data['difficulty'])
    output_file.write('%s;%s;%s;%s;' % (
             keywords, grade, relevance, difficulty))

def print_khan_data(khan_data, output_file):
    """
    Write data from Khan API for one content item to a file
    | id | title | description | URL |
    """
    title = khan_data['translated_title'].strip().replace(';',',').replace('\n', ' ')
    desc = khan_data['translated_description'].strip().replace(';',',').replace('\n', ' ')
    output_file.write('%s;%s;%s;%s;' % (
             khan_data['id'], title, desc, khan_data['ka_url']))

def print_bakalari_data(bakalari_data, content_type, output_file):
    """
    Write fixed Bakalari fields for one content item to a file
    | Předmět | Jazyk - mluvené slovo | Jazyk - titulky | Jazyk - texty |
    | Kulturně závislý obsah | Typ materiálu | Způsob využití |
    | Dodavatel | Přístup | Autor |
    """
    output_file.write('%s;%s;%s;%s;%s;%s;%s;%s;%s;%s' % (
             bakalari_data['SUBJECT'], bakalari_data['lang_audio'], bakalari_data['lang_subs'], bakalari_data['lang_text'],
             bakalari_data['CULTURE'], bakalari_data['TYPE'][content_type], bakalari_data['USAGE'][content_type],
             bakalari_data['DODAVATEL'], bakalari_data['ACCESS'], bakalari_data['AUTHOR']))


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
    related_unique_keywords = set()
    related_grades = []
    related_relevances = []
    related_difficulties = []
    for i in related_video_ids:
        if i in linked_data.keys():
            d = linked_data[i]
            related_grades.append(int(d['grade']))
            related_relevances.append(int(d['relevance']))
            related_difficulties.append(int(d['difficulty']))
            keywords = d['keywords'].split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                keyword = fix_typos_in_keyword(keyword)
                related_unique_keywords.add(keyword)

    related_grade = 0
    # Pick the highest related data
    if len(related_grades) != 0:
        related_grades.sort(reverse=True)
        related_grade = related_grades[0]
        if related_grades[0] != related_grades[-1] and opts.debug:
            eprint('WARNING: Incompatible related grades for exercise ', c['slug'])
            eprint('Video IDS:', related_video_ids)
            eprint('Lowest and highest grade:', related_grades[-1], related_grades[0])
            eprint('Grade difference:', related_grades[0] - related_grades[-1])

    related_relevance = 0
    if len(related_relevances) != 0:
        related_relevances.sort(reverse=True)
        related_relevance = related_relevances[0]

    related_difficulty = 0
    if len(related_difficulties) != 0:
        related_difficulties.sort(reverse=True)
        related_difficulty = related_difficulties[0]

    related_data = {
        'keywords': related_unique_keywords,
        'grade': related_grade,
        'relevance': related_relevance,
        'difficulty': related_difficulty
    }
    return related_data


def stringify_keywords(keyword_set):
    keywords = ''
    for k in keyword_set:
        keywords += k + ','
    keywords = keywords.rstrip(',')
    return keywords

def stringify_number(number):
    if number < 0:
        print("ERROR: Invalid number %i" % number)
        sys.exit(1)
    elif number == 0:
        return ''
    else:
        return str(number)

def update_related_data(rel_data, new_data):
    for key in rel_data.keys():
        if key == 'keywords':
            # Union of sets
            rel_data[key].update(new_data[key])
        else:
            if new_data[key] > rel_data[key]:
                rel_data[key] = new_data[key]

def get_unit_test_link(unit):
    unit_url = unit['ka_url']
    unit_slug = unit['slug']
    unit_test_url = "%s/test/%s-unit-test?modal=1" % (unit_url, unit_slug)
    return unit_test_url

def get_unit_test_title(unit):
    return "Souhrnný test ke kapitole: " + unit['translated_title']

def get_unit_test_description(unit):
    # TODO: What should the description be?
    # return "Obsahuje příklady z lekcí: " + get_lesson_titles(unit)
    return unit['translated_description']

# Filter out unlisted content
def get_listed_content(content, listed_content_slugs):
    listed_content = []
    # This looks weird cause our listed_content_file contains either slug or id
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
#   topic_title  = opts.subject
#   content_type = opts.content.lower()
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
    listed_content_slugs = utils.read_listed_content_slugs()
    listed_topic_slugs = utils.read_listed_topic_slugs()
    # External data from Bakalari linkers
    khan_video_linked_data = read_linked_data()

    related_data_prototype = {
        'keywords': set(),
        'grade': 0,
        'relevance': 0,
        'difficulty': 0
    }

    OUTPUT_FNAME = 'bakalari_khan_export_%s_%s.csv' % (topic_title.replace(' ', '_').lower(), content_type)
    f = open(OUTPUT_FNAME, 'w')
    print_header(f)

    unique_content_ids = set()
    units = []

    khan_tree.get_units(units, subtree)

    for unit in units:
        if unit['slug'] not in listed_topic_slugs:
            continue
        lessons = []
        unit_data = related_data_prototype
        khan_tree.get_lessons(lessons, unit)

        # TODO: Skip unlisted lessons, but hopefully not necessary
        for lesson in lessons:
            content = []
            lesson_data = related_data_prototype
            kapi_tree_get_content_items(lesson, content, content_type)

            # Filter out unlisted content first
            listed_content = get_listed_content(content, listed_content_slugs)

            # Listed content can contain duplicities from previous lessons,
            # but that is okay because we want the linked data from them!
            for c in listed_content:
                exercise_data = get_related_data(c, khan_video_linked_data)
                update_related_data(lesson_data, exercise_data)

            # Filter out duplicities now!
            unique_content = get_unique_content(listed_content, unique_content_ids)

            # Print lesson link if the lesson is not empty
            # If lessons contains only duplicates, we do not print it
            if len(unique_content) > 0:
                print_bakalari_link(lesson, lesson_data, BAKALARI_DATA, f)

            # Print links for individual content items
            for c in unique_content:
                exercise_data = get_related_data(c, khan_video_linked_data)
                print_bakalari_link(c, exercise_data, BAKALARI_DATA, f)

            update_related_data(unit_data, lesson_data)

        # Print UNIT TEST
        # A dirty hack, we want to link to a Unit TEST, not the Unit itself
        unit['ka_url'] = get_unit_test_link(unit)
        unit['translated_title'] = get_unit_test_title(unit)
        unit['translated_description'] = get_unit_test_description(unit)
        print_bakalari_link(unit, unit_data, BAKALARI_DATA, f)

    f.close()
    print("Number of retrieved content items = ", len(unique_content_ids))
