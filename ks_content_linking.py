#!/usr/bin/env python3
from kapi import *
from utils import *
import argparse, sys
import time
import json
import psycopg2

# Figure out how to connect to PSQL from 
# http://www.postgresqltutorial.com/postgresql-python/connect/

def read_cmd():
   """Reading command line options."""
   desc = "Program for linking CS-Khan content for EMA reputation system."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('-p','--password', dest = 'password', required = False, help = 'Postgres password')
   parser.add_argument('-s','--schema', dest='schema', default = 'root', help = 'Link given schema.')
   parser.add_argument('-a','--all', dest = 'all', action = 'store_true', help = 'Print all available schemas')
   # TODO: Add verbose parameter
   return parser.parse_args()

# Currently, article type does not seem to work.
CONTENT_TYPES = ['video']

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
    # TODO: Update these for KS schemas
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

def ema_print_schema_content(schema, content):
    ema_content = []
    unique_content_ids = set()
    content_type = 'video'

    schema_subject_map = {
        'organicka_chemie': 'chemie',
        'obecna_chemie': 'chemie',
        'fyzikalni_chemie': 'chemie',
        'rychlokurz_chemie': 'chemie'
    }

    subject = schema_subject_map[schema]

    for v in content:

        if v['id'] in unique_content_ids:
            eprint("Found in previous schemas, skipping: ")
            continue
        else:
            unique_content_ids.add(v['id'])

        try:
          item = {
            # Key items
            'id': v['id'],
            'url': v['url'],
            'nazev': v['title'],
            'popis': v['description'],
            # Fixed items
            'autor': EMA_OPTIONAL_DATA['autor'],
            'jazyk': EMA_OPTIONAL_DATA['jazyk'],
            'dostupnost': EMA_OPTIONAL_DATA['dostupnost'],
            'licence': EMA_OPTIONAL_DATA['licence']['cc-by-nc-sa'],
            # Optional fields
            'typ': EMA_OPTIONAL_DATA['typ'][content_type],
            # TODO: Uncomment this in final version
            #'stupen_vzdelavani': EMA_OPTIONAL_DATA['stupen_vzdelavani'][schema],
            #'vzdelavaci_obor': EMA_OPTIONAL_DATA['vzdelavaci_obor'][subject],
            #'gramotnost': EMA_OPTIONAL_DATA['gramotnost'][subject],
          }

          ema_content.append(item)

        except:
            eprint('Key error!')
            eprint(v)
            raise
 
    with open('ks_%s_%s.json' % (schema.replace('-', '_').lower(), content_type), 'w', encoding = 'utf-8') as out:
        out.write(json.dumps(ema_content, ensure_ascii=False))

    print("Number of EMA %s in %s = %d" % (content_type, schema, len(ema_content)))

def connect_ks(psswd):
    db_name = 'khanovaskola'
    conn = psycopg2.connect(host="localhost", database = db_name, user="postgres", password = psswd)
    cur = conn.cursor()
    print('PostgreSQL database version:')
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(db_version)
    cur.close()
    return conn


def print_schemas(connection):
    cur = connection.cursor()
    schema_id = 2
    sql = "SELECT id, title FROM schemas ORDER BY id"
    cur.execute(sql)
    print("Number of schemas is %s" % (cur.rowcount))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()


def get_schema_content(connection, schema_id):
    if type(schema_id) is not int or schema_id < 1:
        print("ERROR: Invalid schema id")
        print(schema_id)
        sys.exit(1)

    cur = connection.cursor()

    # TODO: Check which JOINS to use to avoid duplicates
    sql = """SELECT ct.id, ct.title, ct.description, ct.youtube_id
            FROM "contents" AS ct 
            JOIN content_block_bridges AS cbb ON ct.id = cbb.content_id
            JOIN blocks ON blocks.id = cbb.block_id
            JOIN block_schema_bridges AS bsb ON bsb.block_id = blocks.id
            JOIN schemas AS sch ON sch.id = bsb.schema_id
            WHERE ct.type = 'video' AND ct.hidden = 'f' AND sch.id = %d
            ORDER BY ct.id""" % (schema_id)

    cur.execute(sql)
    if cur.rowcount < 1:
        print("ERROR: 0 rows in schema id %d" % (schema_id))
        sys.exit(1)
    else:
        print("Found %d videos in schema id %d" % (cur.rowcount, schema_id))
    rows = cur.fetchall()
    cur.close()
    return rows


if __name__ == '__main__':

    opts = read_cmd()
    psswd = opts.password
    schema_title = opts.schema
    # TODO: Schema_title_id_map
    schema_title_id_map = {
            'organicka_chemie': 24
            }
    with open("psql", "r") as f:
        psswd = f.read()
        psswd = psswd[:-1]

    conn = connect_ks(psswd)
    #print_schemas(conn)
    schema_id = schema_title_id_map[schema_title]
    rows = get_schema_content(conn, schema_id)
    videos = []
    for row in rows:
        # TODO: Make prettier URL, include full schema/block path
        url = 'https://khanovaskola.cz/video/%s' % row[3]
        video = {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'url': url
        }
        videos.append(video)
        #print(row)

    ema_print_schema_content(schema_title, videos)

    if conn is not None:
        conn.close()
        print('Database connection closed.')

