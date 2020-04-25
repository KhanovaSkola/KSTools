#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time
import json

def read_cmd():
   """Reading command line options."""
   desc = "Program for computing number and total duration of unique Khan videos per course."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-s','--subject', dest='topic', default = None, help='Count content for a given topic slug.')
   return parser.parse_args()

# TODO: Exercises and articles currently not implemented
CONTENT_TYPES = ['video', 'article', 'exercise']

if __name__ == '__main__':

    opts = read_cmd()
    #topic_title  = opts.subject
    topic_title = 'root'

    khan_tree = KhanContentTree('en', 'video')
    video_tree = khan_tree.get()
    khan_tree = KhanContentTree('en', 'exercise')
    exercise_tree = khan_tree.get()

    all_unique_content_ids = set()

    # Handle duplicities across courses
    # The ordering here is important!
    math_courses = ['Early math', 'Arithmetic', 'Basic geometry', 'Trigonometry', 'Algebra basics', 'Pre-algebra',
            'Algebra I', 'Algebra II', 'High school geometry', 'Precalculus', 'High school statistics', 'AP®︎ Statistics',

            'Differential Calculus', 'Integral Calculus']
    science_courses = ['Chemistry', 'Organic chemistry', 'AP®︎ Chemistry', 'Biology', 'AP®︎ Physics 1', 'Physics', 'AP®︎ Physics 2']

    math_topics = ['algebra-basics', 'alg-complex-numbers', 'imaginary-and-complex-numbers', 'introduction-to-complex-numbers-algebra-2',
            'prob-comb', 'probability-library', 'counting-permutations-and-combinations', 'vectors-precalc', 'conics-precalc',
            'two-var-linear-equations', 'algebra-functions', 'linear-word-problems', 'manipulating-functions','exponential-and-logarithmic-functions']

    physics_topics = ['simple-harmonic-motion-ap', 'ap-mechanical-waves-and-sound',
            'ap-electric-charge-electric-force-and-voltage', 'ap-circuits-topic', 'magnetic-forces-and-magnetic-fields']

    chem_topics = ['atomic-structure-and-properties', 'chemical-reactions-stoichiome', 'electronic-structure-of-atoms',
            'periodic-table', 'chemical-bonds', 'oxidation-reduction',
            'chem-kinetics', 'gases-and-kinetic-molecular-theory', 'states-of-matter-and-intermolecular-forces',
            'chemical-equilibrium', 'acids-and-bases-topic', 'thermodynamics-chemistry']

    print("|Course|total videos|unique videos|duration|total exercises|unique exercises|")
    print('|--|--|--|--|--|--|')
    courses = math_topics + physics_topics + chem_topics
    if opts.topic is not None:
        courses = [opts.topic]
    for course in courses: 
        video_duration = 0 # In seconds
        course_videos = []
        unique_course_videos = []
        course_exercises = []
        unique_course_exercises = []

        subtree = find_ka_topic(video_tree, course)
        kapi_tree_get_content_items(subtree, course_videos, 'video')
        subtree = find_ka_topic(exercise_tree, course)
        kapi_tree_get_content_items(subtree, course_exercises, 'exercise')

        for c in course_videos:
            cid = c['id']
            if cid not in all_unique_content_ids:
                unique_course_videos.append(c)
                all_unique_content_ids.add(cid)
                video_duration += c['duration']

        for c in course_exercises:
            cid = c['id']
            if cid not in all_unique_content_ids:
                unique_course_exercises.append(c)
                all_unique_content_ids.add(cid)
        
        print("|%s|%i|%i|%ih%im|%i|%i" % (course, len(course_videos), len(unique_course_videos), video_duration/3600, video_duration/60 % 60, len(course_exercises), len(unique_course_exercises)) )


    '''
    for v in content:

        if v['id'] not in listed_content and v['slug'] not in listed_content:
            print('Not listed: ' + v['slug'])
            continue

        if v['id'] in unique_content_ids:
            print("Found in previous math course, skipping: ", v['slug'])
            continue
        else:
            unique_content_ids.add(v['id'])

    '''
