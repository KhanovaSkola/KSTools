#!/usr/bin/python3

# Usage example:
# python captions.py --videoid='<video_id>' --name='<name>' --file='<file>' --language='<language>' --action='action'

import httplib2, os, sys, re, datetime
from pprint import pprint

from googleapiclient.discovery import build_from_document
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import logging
logging.basicConfig()

def get_isosplit(s, split):
    if split in s:
        n, s = s.split(split)
    else:
        n = 0
    return n, s

# https://stackoverflow.com/a/64232786/3682277
def parse_isoduration(s):
    """Helper function for parsing video durations"""
    # Remove prefix
    s = s.split('P')[-1]

    # Step through letter dividers
    days, s = get_isosplit(s, 'D')
    _, s = get_isosplit(s, 'T')
    hours, s = get_isosplit(s, 'H')
    minutes, s = get_isosplit(s, 'M')
    seconds, s = get_isosplit(s, 'S')

    # Convert all to seconds
    dt = datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))
    return int(dt.total_seconds())

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Dev Console }} at
# {{ https://console.developers.google.com/ }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
SECRETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../SECRETS"))

CLIENT_SECRETS_FILE = "%s/google_client_secrets.json" % (SECRETS_DIR)

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com
For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  # The credentials will be saved to this file,
  # so we need to sign in only once
  storage = Storage("%s/%s-oauth2.json" % (SECRETS_DIR, os.path.basename(sys.argv[0])))
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  # https://stackoverflow.com/questions/29762529/where-can-i-find-the-youtube-v3-api-captions-json-discovery-document
  with open("%s/youtube-v3-api.json" % os.path.dirname(__file__), "r", encoding = "utf-8") as f:
    doc = f.read()
    return build_from_document(doc, http=credentials.authorize(httplib2.Http()))


# Call the API's captions.list method to list the existing caption tracks.
def list_captions(youtube, video_id, verbose=True):
  results = youtube.captions().list(
    part="snippet",
    videoId=video_id
  ).execute()

  for item in results["items"]:
    id = item["id"]
    name = item["snippet"]["name"]
    language = item["snippet"]["language"]
    if verbose:
        print("Caption track '%s(%s)' in '%s' language." % (name, id, language))

  return results["items"]


# Call the API's captions.insert method to upload a caption track in draft status.
def upload_caption(youtube, video_id, language, name, is_draft, file):
  try:
    insert_result = youtube.captions().insert(
    part="snippet",
    body=dict(
      snippet=dict(
        videoId=video_id,
        language=language,
        name=name,
        isDraft=is_draft
      ),
    ),
    media_mime_type = 'text/xml',
    media_body = file,
    ).execute()
  except HttpError as e:
      print("Got the following error during sub upload, YTID = ", video_id)
      print(e)
      raise

  id = insert_result["id"]
  name = insert_result["snippet"]["name"]
  language = insert_result["snippet"]["language"]
  status = insert_result["snippet"]["status"]
  print("Uploaded caption track '%s(%s) in '%s' language, '%s' status." % (name,
      id, language, status) )
  return True


# Call the API's captions.update method to update an existing caption track's draft status
# and publish it. If a new binary file is present, update the track with the file as well.
def update_caption(youtube, video_id, language, caption_id, is_draft, file):
  try:
    update_result = youtube.captions().update(
    part="snippet",
    body=dict(
      id=caption_id,
      snippet=dict(
        isDraft=is_draft
      )
    ),
    media_mime_type = 'text/xml',
    media_body=file
    ).execute()

  except HttpError as e:
      print("Got the following error during subtitle update")
      print(e)
      raise

  name = update_result["snippet"]["name"]
  isDraft = update_result["snippet"]["isDraft"]
  print("Updated caption track '%s' draft status to be: '%s'" % (name, isDraft))
  if file:
    print("and updated the track with the new uploaded file.")

  return True


# Call the API's captions.download method to download an existing caption track.
def download_caption(youtube, caption_id, tfmt):
  subtitle = youtube.captions().download(
    id=caption_id,
    tfmt=tfmt
  ).execute()

  #print("First line of caption track: %s" % (subtitle))
  with open(caption_id, "wb") as f:
      f.write(subtitle)

# Get full API information about an YT video
def list_video(youtube, youtube_id):
    """https://developers.google.com/youtube/v3/docs/videos/list"""
    response = youtube.videos().list(
	part='snippet,contentDetails,status',
	id=youtube_id).execute()
    snippet = response['items'][0]['snippet']
    pprint(response['items'][0])
    return snippet


# Get specific information for a list of videos
def list_videos(youtube, youtube_ids):
    """https://developers.google.com/youtube/v3/docs/videos/list

    Adapted from Khan codebase in:
    webapp/gcloud/youtube/youtube_api.py
    """
    # Youtube service returns results for ids with trailing
    # whitespaces.  We need to strip it here to make sure that we
    # keep a canonical youtube_id for each video.
    all_youtube_ids = [ytid.strip() for ytid in youtube_ids]

    # The YouTube API will only let us fetch 50 IDs at a time.
    max_results = 50
    data = []
    for i in range(0, len(all_youtube_ids), max_results):
        response = youtube.videos().list(
            part='id,snippet,contentDetails,status',
            id=",".join(all_youtube_ids[i:i + max_results]),
            maxResults=max_results).execute()
        data.extend(response["items"])

    fields = ('title', 'video_id', 'published_at', 'duration', 'lang',
    'has_captions', 'privacy_status', 'license', 'made_for_kids')
    header = "\t".join(fields)
    fmtstring = "\t".join(["%s" for i in fields])
    print(header)
    for video in data:
        snippet = video['snippet']
        details = video['contentDetails']
        status = video['status']
        to_print = {
                'video_id': video['id'],
                'title': snippet['title'],
                'has_captions': details['caption'],
                'published_at': snippet['publishedAt'],
                'duration': parse_isoduration(details['duration']),
                'privacy_status': status['privacyStatus'],
                'license': status['license'],
                'made_for_kids': status['madeForKids'],
        }
        # For some reason, some video are missing this param
        to_print['lang'] = snippet.get('defaultAudioLanguage') or snippet.get('defaultLanguage', '')

        print(fmtstring % tuple([to_print[key] for key in fields]))

    return data


# Get API information about a YT channel
def list_channel(youtube, channel_id):
    """https://developers.google.com/youtube/v3/docs/channels/list"""
    response = youtube.channels().list(
	part='id,snippet,contentDetails',
	id=channel_id).execute()
    snippet = response['items'][0]['snippet']
    pprint(response)
    return snippet


# Get API information about a YT playlist
def list_playlist(youtube, playlist_id):
    """https://developers.google.com/youtube/v3/docs/channels/list"""
    response = youtube.playlists().list(
	part='id,snippet,contentDetails',
	id=playlist_id).execute()
    snippet = response['items'][0]['snippet']
    pprint(response)
    return snippet

# List auto-generated playlists for a given channel
def list_channel_playlists(youtube, channel_id):
    """https://developers.google.com/youtube/v3/docs/channels/list"""
    all_playlists = {}
    response = youtube.channels().list(
	part='contentDetails',
	id=channel_id).execute()
    playlists = response['items'][0]['contentDetails']['relatedPlaylists']
    for pl in playlists:
        title = pl
        playlist_id = playlists[pl]
        all_playlists[title] = playlist_id
        print("%s\t%s" % (playlist_id, title))

    return all_playlists


# List custom playlists
def list_custom_playlists(youtube, channel_id):
    """https://developers.google.com/youtube/v3/docs/channels/list"""
    all_playlists = {}
    response = youtube.playlists().list(
	part='id,snippet',
	channelId=channel_id).execute()
    playlists = response['items']
    for pl in playlists:
        title = pl['snippet']['title']
        playlist_id = pl['id']
        all_playlists[title] = playlist_id
        print("%s\t%s" % (playlist_id, title))

    return all_playlists


# List all uploaded videos for a given channel
# use action=list_video to get a channel id
# unlisted and private videos will be included only
# if we're authenticated as a manager for the channel
def list_all_videos_in_channel(youtube, channel_id):
    playlists = list_channel_playlists(youtube, channel_id)
    playlist_id = playlists['uploads']
    list_all_videos_in_playlist(youtube, playlist_id)


def list_all_videos_in_playlist(youtube, playlist_id, nextPageToken=None):
    """https://developers.google.com/youtube/v3/docs/playlistItems/list"""
    youtube_ids = set()
    response = youtube.playlistItems().list(
	part='id,snippet',
        maxResults=50,
        pageToken=nextPageToken,
	playlistId=playlist_id).execute()
    for video in response['items']:
        snippet = video['snippet']
        title = snippet['title']
        video_id = snippet['resourceId']['videoId']
        youtube_ids.add(video_id)
        print("%s\t%s" % (video_id, title))
    if 'nextPageToken' in response.keys():
        youtube_ids.union(list_all_videos_in_playlist(
                youtube, playlist_id, response['nextPageToken']
                )
        )
    return youtube_ids


if __name__ == "__main__":
  # The "videoid" option specifies the YouTube video ID that uniquely
  # identifies the video for which the caption track will be uploaded.
  argparser.add_argument("--videoid",
    help="Required; ID for video for which the caption track will be uploaded.")
  argparser.add_argument("--videoids-file",
    help="Input file with one ID per row.")
  # The "name" option specifies the name of the caption trackto be used.
  argparser.add_argument("--name", help="Caption track name", default="")
  # The "file" option specifies the binary file to be uploaded as a caption track.
  argparser.add_argument("--file", help="Captions track file to upload")
  # The "language" option specifies the language of the caption track to be uploaded.
  argparser.add_argument("--language", help="Caption track language", default="en")
  # The "captionid" option specifies the ID of the caption track to be processed.
  argparser.add_argument("--captionid", help="Required; ID of the caption track to be processed")
  # The "action" option specifies the action to be processed.
  argparser.add_argument("--action", help="Action: list|list_video|upload|update|download")
  # The "action" option specifies the action to be processed.
  argparser.add_argument("--draft", help="Publish subtitles?", default=False, action='store_true')
  argparser.add_argument("--channelid", help="YouTube Channel ID")
  argparser.add_argument("--playlistid", help="YouTube playlist ID")


  args = argparser.parse_args()
  SUPPORTED_ACTIONS = (
          # actions related to captions
          'upload_captions', 'download_captions', 'update_captions',
          'list_captions',
          # actions related to videos
          'list_video', 'list_many_videos',
          # actions related to channels
          'list_channel', 'list_channel_videos', 'list_channel_playlists',
          # actions related to playlists
          'list_playlist', 'list_playlist_videos')

  if args.action not in SUPPORTED_ACTIONS:
      print("Available actions:", SUPPORTED_ACTIONS)
      exit("Unsupported action = %s" % args.action)

  if (args.action in ('upload_captions', 'list_captions', 'list_video')):
    if not args.videoid:
          exit("Please specify videoid using the --videoid= parameter.")

  if args.action in ('list_many_videos'):
    if not args.videoids_file:
          exit("Please specify videoids in a file (one per line), using the --videoids-file=fname parameter.")

  if (args.action in ('update_captions', 'download_captions', 'delete_captions')):
    if not args.captionid:
          exit("Please specify captionid using the --captionid= parameter.")

  if (args.action in ('list_channel', 'list_channel_videos', 'list_channel_playlists')):
    if not args.channelid:
          exit("Please specify channel ID using the --channelid= parameter.")

  if (args.action in ('list_playlist', 'list_playlist_videos')):
    if not args.playlistid:
          exit("Please specify playlist ID using the --playlistid= parameter.")

  if args.action == 'upload':
    if not args.file:
      exit("Please specify a caption track file using the --file= parameter.")
    if not os.path.exists(args.file):
      exit("Please specify a valid file using the --file= parameter.")

  if args.action in ('upload_captions', 'update_captions', 'delete_captions'):
      # NOTE(danielhollas): this is just a precautionary measure
      if args.language != 'cs':
          exit("We do not support upload to other languages besides Czech!")


  youtube = get_authenticated_service(args)

  youtube_ids = set()
  if args.videoids_file:
    with open(args.videoids_file, 'r') as f:
        youtube_ids = set(f.read().split('\n'))
        youtube_ids.remove('')
  elif args.videoid:
      youtube_ids = set([args.videoid])

  YTID_REGEX = r'^[a-zA-Z0-9_-]{11}$'
  for youtube_id in youtube_ids:
    if not re.fullmatch(YTID_REGEX, youtube_id):
      exit("Invalid YouTube ID: %s" % youtube_id)

  try:
    # Channel actions
    if args.action == 'list_channel':
        list_channel(youtube, args.channelid);
    elif args.action == 'list_channel_playlists':
        list_channel_playlists(youtube, args.channelid);
        list_custom_playlists(youtube, args.channelid);
    elif args.action == 'list_channel_videos':
        list_all_videos_in_channel(youtube, args.channelid);
    # Playlist actions
    elif args.action == 'list_playlist':
        list_playlist(youtube, args.playlistid);
    elif args.action == 'list_playlist_videos':
        list_all_videos_in_playlist(youtube, args.playlistid);
    # Video actions
    elif args.action == 'list_video':
        list_video(youtube, args.videoid)
    # Bulk listing specific data for videos
    elif args.action == 'list_many_videos':
        list_videos(youtube, youtube_ids)
    # Caption actions
    elif args.action == 'upload_captions':
        upload_caption(youtube, args.videoid, args.language, args.name, args.draft, args.file)
    elif args.action == 'download_captions':
        download_caption(youtube, args.captionid, 'srt')
    elif args.action == 'update_captions':
        update_caption(youtube, args.videoid, args.language, args.captionid, args.draft, args.file);
    elif args.action == 'list_captions':
        list_captions(youtube, youtube_id)

  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
