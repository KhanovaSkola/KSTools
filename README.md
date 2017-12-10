# AmaraUpload
Python scripts for work with Amara, Khan Academy and YouTube APIs.
There are 3 modes of operation, depending on the source of the subtitles.
You can get the subtitles from YouTube, or upload subtitles from a file, or copy subtitles between Amara videos.

The format of the input file depends on the mode of operation.
(see sample_input.txt)

=================================================================================================

You need an Amara account. To authenticate, you need the Amara Api key and username.
(see sample_credentials.txt) 
Amara API can be found in Settins-->Account-->API Access (bottom-right corner)

=================================================================================================

amara_api.py    	Collection of basic Amara API calls


amara_upload.py     	Script for uploading subtitles to Amara.
		Type './amara_upload.py -h' to get help.

amara_download.py	Downloading subtitles from Amara or YouTube.

kapi.py			Basic KA API calls.


=================================================================================================

For downloading subtitles from YouTube, you need the command-line tool youtube-dl.
https://github.com/rg3/youtube-dl

=================================================================================================
To synchronize all KA videos subtitles from YouTube to Amara:

1] Download the KA tree:
	./download_KAtree.py -d

2] Upload subtitles for a given language, that are on YouTube, but have no revision on Amara
/usr/bin/time ../sync_subs_yt2amara.py -l en -c ../myapi_amara.txt allvideos_ids.dat > sync.log 2> sync.log.err &


================================================================================================
If you need to connect via proxy server, the easiest thing to do on Linux is to define the variable HTTPS_PROXY.
If you have BASH:

$ export HTTPS_PROXY="http://your_proxy.com:3128"

https://stackoverflow.com/questions/29762529/where-can-i-find-the-youtube-v3-api-captions-json-discovery-document


# Syncing subtitles from Amara to YouTube in bulk
./sync_subs_amara2yt.py -l cs -c DATA/myapi_amara.txt -g DATA/myapi_google.txt DATA/KS_allYTID.test.csv -d ';' -v -u

https://stackoverflow.com/questions/29762529/where-can-i-find-the-youtube-v3-api-captions-json-discovery-document

https://console.developers.google.com/apis/credentials?project=khan-academy-youtube-subtitles
