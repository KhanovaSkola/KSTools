#!/usr/bin/env python3
import kapi
import utils as u
import argparse, sys
import time

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for printing Khan Academy content tree into CSV file."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-s','--subject', dest = 'subject', default = 'root',
           help = 'Print content for a given domain/subject.')
   parser.add_argument('-c','--content', dest = 'content_type', required = True,
           help = 'Which kind of content should we print? Options: video|exercise|article|topic')
   parser.add_argument('-p','--print-slugs', dest = 'list', default = False, action = "store_true",
           help = 'Only list topic names within given domain/subject/topic.')
   parser.add_argument('-l', '--lang', dest = 'lang', default = 'en',
           help = 'Language of the topic tree. (US by default)')
   return parser.parse_args()

# Currently, article type does not seem to work.
AVAILABLE_CONTENT_TYPES = ['video', 'article', 'exercise', 'topic']

def print_articles(tree, locale):
    khan_api = kapi.KhanAPI(locale)
    khan_tree = kapi.KhanContentTree(locale, 'topic')
    lessons = []
    table_rows = []

    khan_tree.get_lessons(lessons, tree)

    for lesson in lessons:
        print("Downloading articles from lesson: %s" % lesson['title'])
        table_rows.append('%s\n' % lesson['title'])
        article_ids = get_article_ids_from_lesson(lesson)
        for i in article_ids:
            article = khan_api.download_article(i)
            tp_link = kapi.create_tp_link(article['node_slug'])
            ka_link = 'https://www.khanacademy.org' + article['relative_url']
            trow ="%s;%s;%s\n" % (article['title'], ka_link, tp_link)
            table_rows.append(trow)
    return table_rows

def get_article_ids_from_lesson(lesson):
    ids = []
    for content_item in lesson['child_data']:
        if content_item['kind'] == 'Article':
            ids.append(content_item['id'])
    return ids


if __name__ == "__main__":

    opts = read_cmd()
    subject_title  = opts.subject
    lst = opts.list

    if opts.content_type not in AVAILABLE_CONTENT_TYPES:
        print("ERROR: invalid content type argument:", opts.content_type)
        print("Possibilities are:", AVAILABLE_CONTENT_TYPES)
        exit(1)

    if opts.content_type == "article":
        tree_type = 'topic'
    else:
        tree_type = opts.content_type

    khan_tree = kapi.KhanContentTree(opts.lang, tree_type)
    tree = khan_tree.get()

    if subject_title == 'root':
        subtree = tree
    else:
        subtree = kapi.find_ka_topic(tree, subject_title)

    # The following is helpful to determine where things are
    if lst:
        if subtree is not None:
            print("Printing dictionary for topic ", subject_title)
            u.print_dict_without_children(subtree)
            #print("=============================")
            print("Listing topic children for %s" % (subject_title))
            u.print_children_titles(subtree)
            sys.exit(0)
        else:
            print("ERROR: Could not find topic titled: "+subject_title)
            sys.exit(1)


    # Print unique content items to csv file by default
    if  opts.content_type in ('video', 'exercise'):
        ids = set()
        data = []
        keys = ()
        if opts.content_type == 'video':
            keys = ('youtube_id', 'readable_id', 'duration')
        else:
            keys = ('node_slug', 'title')

        khan_tree.get_unique_content_data(ids, data, keys, subtree)
 
        with open("unique_content.tsv", "w") as f:
            for v in data:
                line = ''
                for k in keys:
                    line += "%s\t" % (v[k])
                line += '\n'
                f.write(line)

    
    # Making large table of data for a given subject
    # Note that this unfortunately only work at the subject level,
    # Not for e.g. individual topics or tutorials
    # We should fix function kapi_tree_print_full to be more general
    content_lines = []
    date = time.strftime("%Y-%m-%d")
    
    if opts.content_type == 'article':
        content_lines = print_articles(subtree, opts.lang)
    else:
        kapi.kapi_tree_print_full(subtree, content_lines)

    # TODO: Add info about whether video is dubbed or not,
    # Need a separate call to kapi.download_video
    
    # NEED to filter out subtitled videos that should be dubbed probably check manually in relevant subject
    # Maybe we should also add filtering here based on what is INDEXABLE

    filename = opts.content_type + "_" + u.format_filename(subject_title) + "_" + date + ".csv"
    with open(filename, "w", encoding = 'utf-8') as f:
        for c in content_lines:
            f.write(c)

