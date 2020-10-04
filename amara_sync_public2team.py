#!/usr/bin/env python3
import argparse, sys, requests
from pprint import pprint
from api.amara_api import Amara
from utils import eprint, download_yt_subtitles
from time import sleep

def read_cmd():
   """Function for reading command line options."""
   desc = "Program for syncing subtitles to Khan Academy Team Amara."
   parser = argparse.ArgumentParser(description=desc)
   parser.add_argument('input_file',metavar='INPUT_FILE', help='Text file containing YouTube IDss.')
   parser.add_argument(
           '-l', '--lang', dest = 'lang',
           required = True,
           help='What language?')
   parser.add_argument(
           '--sub-format', dest = 'sub_format',
           required = False, default = 'vtt',
           help='What language?')
   parser.add_argument(
           '-f', '--from-files', dest = 'file_dir',
           required = False, default = None,
           help='Upload subtitles from files, from given folder.')
   parser.add_argument(
           '-y', '--from-youtube', dest = 'yt_download',
           required = False, default = False, action = 'store_true',
           help='Download subtitles from YT and upload to Team Amara.')
   parser.add_argument(
           '-a', '--from-amara', dest = 'amara_public_download',
           required = False, default = False, action = 'store_true',
           help='Download subtitles from Public Amara and upload to Team Amara.')
   parser.add_argument(
           '-p', '--publish',
           dest = 'publish', default=False, action = 'store_true',
           help='Are subtitles complete?')
   parser.add_argument(
           '-s', '--sleep', dest = 'sleep_int',
           required = False, type = float, default = -1,
           help='Sleep interval (seconds)')
   return parser.parse_args()


opts = read_cmd()
lang = opts.lang

AMARA_TEAM = "khan-academy"
AMARA_SUBTITLER = 'danekhollas'
AMARA_REVIEWER = 'dhbot'
SUB_FORMAT = opts.sub_format

PUBLISH_SUBTITLES = opts.publish
# When downloading from YT, do a publish automatically,
# since they are already published there.
# Though, maybe if people want to keep editing them, it would be better to
# leave them unpublished? Maybe.
if opts.yt_download:
    PUBLISH_SUBTITLES = True

# List ytids may also contain filenames
ytids = []
# Reading file with YT id's
with open(opts.input_file, "r") as f:
    for line in f:
        ytids.append(line.split())

amara = Amara(AMARA_SUBTITLER)
amara_review = Amara(AMARA_REVIEWER)

def check_upload_success(response, sub_version_old):
    sub_version_new = response['version_number']
    if sub_version_new != sub_version_old + 1:
        eprint("ERROR: Something went wrong during subtitle upload")
        eprint(r)
        sys.exit(1)

def compare_work_status(work_status, expected_work_status):
    if work_status != expected_work_status:
        eprint("ERROR: Unexpected work status!")
        eprint("Expected: %s Got: %s" % (expected_work_status, work_status))
        sys.exit(1)

def check_work_status(amara_id, lang, team, expected_status):
    r = amara.list_subtitle_requests(amara_id, lang, team)
    if r['meta']['total_count'] == 0 \
            or r['objects'][0]['work_status'] != expected_status:
        eprint("Unexpected response, expected work_status==%s" %
                expected_status)
        pprint(r)
        sys.exit(1)

def download_subs_from_public_amara(amara, ytid, lang):
    """Returns tuple subtitles downloaded from Public Amara"""

    # Check whether the video is already on Amara
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid
    amara_response = amara.check_video(video_url)
    if amara_response['meta']['total_count'] == 0:
        eprint("ERROR: Source video is not on Public Amara! YTID=%s" % ytid)
        sys.exit(1)

    amara_id_public = amara_response['objects'][0]['id']
    amara_title = amara_response['objects'][0]['title']
    print("\n######################################\n")
    print("Title: %s YTID=%s" % (amara_title, ytid))

    # Check whether subtitles for a given language are present,
    is_present, sub_version_public = amara.check_language(amara_id_public, lang)
    if is_present:
        print("Subtitle revision %d (Public Amara)" % sub_version_public)
    else:
        eprint("ERROR: Amara does not have subtitles in %s language for this \
                video!" % lang)
        sys.exit(1)
 
    # Download subtitles from Public Amara for a given language
    subs = amara.download_subs(amara_id_public, lang, SUB_FORMAT)
    return subs, sub_version_public

def read_subs_from_file(ytid, lang, dirname, sub_format):
    fname = "%s/%s.%s.%s" % (dirname, ytid, lang, sub_format)
    print("Reading subtitles from %s" % fname)
    with open(fname, 'r') as f:
        subs = f.read()
    return subs

def replace_double_spaces(subs):
    return subs.replace('  ',' ');

# Main loop
for i in range(len(ytids)):
    if len(ytids[i]) == 0:
        print("")
        continue
    ytid = ytids[i][0]

    sys.stdout.flush()
    sys.stderr.flush()

    # 1. DOWNLOAD SUBS
    if opts.file_dir is not None :
        subs = read_subs_from_file(ytid, lang, opts.file_dir, SUB_FORMAT)
    elif opts.yt_download:
        backup_dir = "subs_backup_%s" % lang
        subs = download_yt_subtitles(lang, SUB_FORMAT, ytid, backup_dir)
    elif opts.amara_public_download:
        subs = download_subs_from_public_amara(amara, ytid, lang)
    else:
        print("ERROR: You didn't specify the subtitle source")
        sys.exit(1)

    # 1.5 Correct common mistakes
    # Remove double spaces between words
    subs = replace_double_spaces(subs)

    # Trying to reduce E 429
    if opts.sleep_int > 0:
        sleep(opts.sleep_int)

    # 2. UPLOAD TO PRIVATE KHAN ACADEMY AMARA
    # Check whether the video is already on Amara
    video_url = 'https://www.youtube.com/watch?v=%s' % ytid
    amara_id_private = None
    amara_response = amara.check_video(video_url, AMARA_TEAM)
    for r in amara_response['objects']:
        if r['team'] == AMARA_TEAM:
            amara_id_private = r['id']

    if not amara_id_private:
        eprint("ERROR: Video is not on Khan Academy Amara! YTID=%s" % ytid)
        #print("Video not found, skipping..")
        #continue
        sys.exit(1)

    is_present, sub_version_private = amara.check_language(amara_id_private, opts.lang)
    if is_present:
        print("Subtitle revision %d (Team Amara)" % sub_version_private)

    # Check whether video has complete subtitles on Amara Team or not
    r = amara.list_subtitle_requests(amara_id_private, opts.lang, AMARA_TEAM)
    if r['meta']['total_count'] == 0:
        # If video does not have subtitle request, and already has
        # subs for given language, they are already hopefully marked as complete,
        # so we should be able to upload directly without fanfare

        # However, if the video has no subtitle revision and no subtitle
        # request, we'll likely fail here.
        if sub_version_private < 1:
            print("Warning: did not find subs revision and no subs request")
        else:
            print("Video already has published subtitles, uploading new version...")

        print(amara.list_actions(amara_id_private, opts.lang))
        # DH TEST: Using amara_review here to try to cheat the Error 429
        r = amara_review.upload_subs(amara_id_private, lang, PUBLISH_SUBTITLES, subs, SUB_FORMAT)
        check_upload_success(r, sub_version_private)
        print(amara.list_actions(amara_id_private, opts.lang))
        continue

    elif r['meta']['total_count'] > 1:

        eprint("Unexpected response")
        eprint(r)
        sys.exit(1)

    else:
        # Here comes the tricky part, we need to deal with Amara workflow
        subs_info = r['objects'][0]
        pprint(subs_info)
        job_id = subs_info['job_id']
        work_status = subs_info['work_status']

        if work_status in ('needs-subtitler', 'being-subtitled'):
            if subs_info['work_status'] == 'being_subtitled':
                print("Subtitler %s is already working on this video." % subs_info['subtitler']['username'])
                print("Reassigning, uploading new subtitle version and marking them ready for review")

            print("Assigning subtitler %s" % AMARA_SUBTITLER)
            r = amara.assign_subtitler(job_id, AMARA_TEAM)
            compare_work_status(r['work_status'], 'being-subtitled')
            is_completely_subtitled = True
            # If we do not want them published,
            # we will leave them to the reviewer
            print("Uploading new subtitles, complete=%s" %
                    is_completely_subtitled)
            r = amara.upload_subs(amara_id_private, lang, \
                    is_completely_subtitled, subs, SUB_FORMAT)

            # If we want subtitles to be published, we need to assign reviewer
            # and Endorse them
            if PUBLISH_SUBTITLES:
                print("Assigning reviewer %s" % AMARA_REVIEWER)
                r = amara_review.assign_reviewer(job_id, AMARA_TEAM)
                compare_work_status(r['work_status'], 'being-reviewed')
                r = amara_review.mark_subtitles_complete(job_id, AMARA_TEAM)
                compare_work_status(r['work_status'], 'complete')
                continue
        
        elif work_status == 'needs-reviewer':
            if not PUBLISH_SUBTITLES:
                print("Video already has subtitles that needs review. \
Will upload new version and mark it as ready for review.")

            print("Assigning reviewer %s" % AMARA_REVIEWER)
            r = amara_review.assign_reviewer(job_id, AMARA_TEAM)
            compare_work_status(r['work_status'], 'being-reviewed')

            print("Uploading new subtitles, complete=%s" % PUBLISH_SUBTITLES)
            r = amara_review.upload_subs(amara_id_private, lang, PUBLISH_SUBTITLES, subs, SUB_FORMAT)
            check_upload_success(r, sub_version_private)
            # If the video is not complete, let's unassign the reviewer
            if not PUBLISH_SUBTITLES:
                print("Unassigning reviewer")
                r = amara_review.unassign_reviewer(job_id, AMARA_TEAM)
                compare_work_status(r['work_status'], 'needs-reviewer')
            else:
                check_work_status(amara_id_private, opts.lang, AMARA_TEAM, 'complete')
            continue


        elif work_status == 'being-reviewed':
            if not PUBLISH_SUBTITLES:
                print("Subtitles already under review, unassigning reviewer.")
                print("New subtitles will NOT be uploaded")
                r = amara_review.unassign_reviewer(job_id, AMARA_TEAM)
                compare_work_status(r['work_status'], 'needs-reviewer')
                continue

            print("Subtitles already under review, assigning new reviewer %s" % AMARA_REVIEWER)
            r = amara_review.assign_reviewer(job_id, AMARA_TEAM)
            print("Uploading new subtitles, complete=%s" % PUBLISH_SUBTITLES)
            r = amara_review.upload_subs(amara_id_private, lang, PUBLISH_SUBTITLES, subs, SUB_FORMAT)
            check_upload_success(r, sub_version_private)
            check_work_status(amara_id_private, opts.lang, AMARA_TEAM, 'complete')

        elif work_status == 'complete':
            print("Subtitles already complete")
            if PUBLISH_SUBTITLES:
                print("Uploading new subtitles, complete=%s" % PUBLISH_SUBTITLES)
            else:
                print("Uploading new version anyway")
            r = amara.upload_subs(amara_id_private, lang, PUBLISH_SUBTITLES, subs, SUB_FORMAT)
            check_upload_success(r, sub_version_private)
            check_work_status(amara_id_private, opts.lang, AMARA_TEAM, 'complete')
            continue

        else:
            print("Unknown subtitle status, not sure what to do")
            sys.exit(1)


