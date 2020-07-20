# KSTools

TODO: Beware, this README is seriously out-of-date. :-(

Python scripts for work with Amara, Khan Academy and YouTube APIs.

---
#### Dependencies

 - Python 3
 - youtube-dl
 
For downloading subtitles from YouTube, you need the command-line tool youtube-dl.
https://github.com/rg3/youtube-dl
(in priciple, we could implement this via YouTube API, but each download takes a lot of API points,
so it is better to use youtube-dl for larger operations)

You need an Amara account. To authenticate, you need the Amara Api key and username.
Amara API can be found in Settins-->Account-->API Access (bottom-right corner)

---
### Source code

amara_api.py    	Collection of basic Amara API calls


amara_upload.py     	Script for uploading subtitles to Amara.
		Type './amara_upload.py -h' to get help.

amara_download.py	Downloading subtitles from Amara or YouTube.

map_ytid2amaraid.py     Produce links to Amara editor from list of YouTube IDs


### Syncing subtitles from Amara to YouTube in bulk

    ./sync_subs_amara2yt.py -l cs ytids.txt  

(add `-u` to overwrite existing subtitles)

    cat  ytvideo_missing.dat captions_on_yt.cs.dat yt_upload_forbidden.cs.dat amarasubs_missing.cs.dat >> sync_amara2yt_skip.cs.dat

https://stackoverflow.com/questions/29762529/where-can-i-find-the-youtube-v3-api-captions-json-discovery-document

https://console.developers.google.com/apis/credentials?project=khan-academy-youtube-subtitles


### Other tips
If you need to connect via proxy server, the easiest thing to do on Linux is to define the variable HTTPS_PROXY.
If you have BASH:

$ export HTTPS_PROXY="http://your_proxy.com:3128"

