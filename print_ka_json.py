#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time
import json

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for downloading and printing Khan Academy content tree." 
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-d','--download',dest='download',default=False,action="store_true", help='Download most up-to-date full tree?')
   parser.add_argument('-s','--subject', dest='subject', default='root', help='Print full tree for a given domain/subject.')
   parser.add_argument('-c','--content', dest='content', default="", help='Which kind of content should we download? Options: video|exercise|article|topic')
   parser.add_argument('-l','--list', dest='list', default=False,action="store_true", help='Only list topic names within given domain/subject/topic.')
   return parser.parse_args()

# Currently, article type does not seem to work.
content_types = ["video", "article", "exercise", "topic"]


def print_children_titles(content_tree):
    for child in content_tree["children"]:
       pprint(child['title'])


def print_dict_without_children(dictionary):
    for k in dictionary.keys():
        if k != 'children':
            print(k, dictionary[k])


if __name__ == "__main__":

    opts = read_cmd()
    download = opts.download
    topic_title  = opts.subject
    content_type = opts.content.lower()
    lst = opts.list

    if content_type not in content_types:
        print("ERROR: content argument:", opts.content)
        print("Possibilities are:", content_types)
        exit(1)

    if download:
        tree = kapi_download_topictree(content_type)
        if tree != None:
            #save_obj_text(tree, "KAtree_"+what+"_txt")
            save_obj_bin(tree, "KAtree_" + content_type + "_bin")
        else:
            tree = load_ka_tree(content_type, content_types)
    else:
        #tree = load_obj_bin("KAtree_"+what+"_bin")
        tree = load_ka_tree(content_type, content_types)

    # Pick just concrete topic from KA tree
    subtree = find_ka_topic(tree, topic_title)
    if not subtree:
        print("ERROR: Could not find subtree for course: %s\n" % (topic_title))
        # DH hack
        subtree = tree
        #sys.exit(1)

    # TODO: We need to take care of the duplicates
    content = []
 
    # TODO: Filter out only given content type
    #kapi_tree_get_content_items(subtree, content, content_type)
    kapi_tree_get_content_items(subtree, content, content_type)
    pprint(content[0].keys())
    pprint(content[0]["youtube_id"])
    pprint(content[0]["translated_youtube_id"])
    rvp_content = []

    # TODO: compactify all these dicts...
    courses = {
        "Early math": "early",
        "Arithmetic": "arith",
        "Trigonometry": "trig",
        "Music": "music",
        "Cosmology and astronomy": "astro"
    }

    try:
        course = courses[topic_title]
    except:
        print("Invalid course!")
        raise
    
    ppuc_types = {
        "video": "8-VI",
        "exercise": "8-IC",
        "article": "8-CL"
    }

    subjects = {
        "math": "9-03",
        "music": "9-11",
        "astro": "9-9, 9-10" # Not clear whether I can do this
    }

    subject_topic_map = {
        "music": subjects["music"],
        "astro": subjects["astro"],
        "early": subjects["math"],
        "arith": subjects["math"],
        "trig": subjects["math"]
    }

    licenses = {
        "cc-by-nc-nd": "1-CCBYNCND30",
        "cc-by-nc-sa": "1-CCBYNCSA30",
        "cc-by-sa": "1-CCBYSA30",
        "yt-standard": "1-OST"
    }

    stupen = {
        "early": "2-Z",
        "arith": "2-Z",
        "trig": "2-G",
        "music": "2-NU",
        "astro": "2-NU"
    }

    ppuc_grades = {
        "early": "3-Z13",
        "arith": "3-Z45", # Not sure about this...
        "trig": "3-SS",
        "music": "3-NU",
        "astro": "3-NU"
    }

    for v in content:

        try:
          item = {
            "id": v["id"],
            "url": v["ka_url"],
            "nazev": v["translated_title"],
            "popis": v["translated_description"],
            "autor": "Khan Academy",
            # KA API gives keywords in EN, commenting out for now....
#            "klicova_slova": v["keywords"],
            "datum_vzniku" : v["creation_date"],
            "jazyk": "5-cs",
#            "otevreny_zdroj": "7-ANO",
            "dostupnost": "7-ANO",
            "vzdelavaci_obor": subject_topic_map[course],
            "typ": ppuc_types[content_type],
            "rocnik": ppuc_grades[course],
            "stupen_vzdelavani": stupen[course],
            "gramotnost": "4-MA" # TODO
          }
          if "ka_user_licence" in v.keys():
             item["licence"] = licenses[v["ka_user_license"]]
          else:
             item["licence"] = licenses["cc-by-nc-sa"] # Let's just take the KA default

          if item["licence"] == "1-OST":
              if v["ka_user_licence"] == "yt-standard":
                item["licence_url"] = "https://www.youtube.com/static?template=terms&gl=CZ"
              else:
                print("Missing license URL!")
                del item["licence"]

          rvp_content.append(item)

        except:
            print("Key error!")
            pprint(v)
            raise
 
    with open("%s_%s.json" % (topic_title.lower(), content_type), "w", encoding = "utf-8") as out:
        out.write(json.dumps(rvp_content, ensure_ascii=False))

    # Printing for Bakalari`
    with open("%s_%s.csv" % (topic_title.lower(), content_type), "w", encoding = "utf-8") as out:
        for c in content:
            out.write("%s;%s;%s;%s\n" % (c["id"], c["youtube_id"], c["translated_youtube_id"],c["ka_url"]))

    pprint(content[-1])

