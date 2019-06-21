#!/bin/bash

# Only for debugging, does not really work cause
# the content ordering in json files seems to be random
function compare_reference {
  course=$1
  ct_type=$2
  fname=`echo $course | sed 's/-/_/g'`
  fname=ka_${fname}_${ct_type}.json
  diff -q $fname ref/$fname
  if [[ $? -ne 0 ]];then
    exit 1
  fi
}

# TODO: Add these as a cmdline parameters
SYNC=false
DOWNLOAD=false
#DEBUG="--debug"
DEBUG=""

if [[ $DOWNLOAD = 'true' ]];then
  ../download_khan_tree.py -l cs -c video
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get exercises for course $course"
    exit 1
  fi
  ../download_khan_tree.py -l cs -c exercise
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get exercises for course $course"
    exit 1
  fi
fi

../ka_content_linking.py -a -c video $DEBUG
if [[ $? -ne 0 ]];then
  echo "ERROR: Could not print videos"
  exit 1
fi

../ka_content_linking.py -a -c exercise $DEBUG
if [[ $? -ne 0 ]];then
  echo "ERROR: Could not print exercises"
  exit 1
fi

if [[ $SYNC != "true" ]];then
  exit 0
fi

# Copy all json files to the server
SRV="/srv/khanovaskola.cz/production/www/ppuc/"

ls *json
mv *json $SRV
if [[ $? -eq 0 ]];then
  echo "SUCCESFUL SYNC OF EMA JSON FILES!"
else
  echo "mv command failed with error code $?"
fi
