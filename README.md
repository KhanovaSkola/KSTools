# KSTools

TODO: Beware, this README is seriously out-of-date. :-(

Python scripts for work with Amara, Khan Academy and YouTube APIs.

---
#### Dependencies

 - Python 3
 - youtube-dl
 
For downloading subtitles from YouTube, you need the command-line tool youtube-dl.
https://github.com/rg3/youtube-dl
(note that this functionality is also implemented via YouTube API, but since it takes your API points
it is better to use youtube-dl for larger operations)

You need an Amara account. To authenticate, you need the Amara Api key and username.
(see sample_credentials.txt) 
Amara API can be found in Settins-->Account-->API Access (bottom-right corner)

---
### Source code

amara_api.py    	Collection of basic Amara API calls


amara_upload.py     	Script for uploading subtitles to Amara.
		Type './amara_upload.py -h' to get help.

amara_download.py	Downloading subtitles from Amara or YouTube.

kapi.py			Basic Khan API calls.

map_ytid2amaraid.py     Produce links to Amara editor from list of YouTube IDs

---
### Syncing Khan video subtitles from YouTube to Amara in bulk

1] Download the Khan Academy topic tree:
    ./download_KAtree.py -d -c video -l en -s root

2] Upload subtitles for a given language, that are on YouTube, but have no revision on Amara
    /usr/bin/time ./sync_subs_yt2amara.py -l en -c SECRETS/myapi_amara.txt unique_content.dat > sync.log 2> sync.log.err &


---

### Syncing subtitles from Amara to YouTube in bulk
./sync_subs_amara2yt.py -l cs -c DATA/myapi_amara.txt DATA/KS_allYTID.test.csv -d ';' -u

cat  ytvideo_missing.dat captions_on_yt.cs.dat yt_upload_forbidden.cs.dat amarasubs_missing.cs.dat >> sync_amara2yt_skip.cs.dat

https://stackoverflow.com/questions/29762529/where-can-i-find-the-youtube-v3-api-captions-json-discovery-document

https://console.developers.google.com/apis/credentials?project=khan-academy-youtube-subtitles


### Other tips
If you need to connect via proxy server, the easiest thing to do on Linux is to define the variable HTTPS_PROXY.
If you have BASH:

$ export HTTPS_PROXY="http://your_proxy.com:3128"

