# AmaraUpload
Python script for uploading subtitles to Amara.
There are 3 modes of operation, depending on the source of the subtitles.
You can get the subtitles from YouTube, or upload subtitles from a file, or copy subtitles between Amara videos.

The format of the input file depends on the mode of operation.
(see sample_input.txt)

=================================================================================================

You need en Amara account. To authenticate, you need a Amara Api key and username.
(see sample_credentials.txt) 
Amara API can be found in Settins-->Account-->API Access (bottom-right corner)

=================================================================================================

amara_api.py    	Collection of basic Amara API calls


amara_upload.py     	Script for uploading subtitles to Amara.
		Type './amara_upload.py -h' to get help.

amara_download.py	Downloading subtitles from Amara.

kapi.py			Basic KA API calls.


=================================================================================================

For downloading subtitles from YouTube, you need the command-line tool youtube-dl.
https://github.com/rg3/youtube-dl

=================================================================================================
To synchronize all KA videos from YouTube to Amara:

1] Download the KA tree:
	./download_KAtree.py

2] Upload subtitles for a given language, that are on YouTube, but have no revision on Amara
/usr/bin/time ../sync_subs_yt2amara.py -l en -c ../myapi_amara.txt allvideos_ids.dat > sync.log 2> sync.log.err &


================================================================================================
If you need to connect via proxy server, the easiest thing to do on Linux is to define the variable HTTPS_PROXY.
If you have BASH:

$ export HTTPS_PROXY="http://your_proxy.com:3128"
