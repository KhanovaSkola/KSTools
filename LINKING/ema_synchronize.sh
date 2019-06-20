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

SYNC=false
DOWNLOAD=false

if [[ $DOWNLOAD = 'true' ]];then
  ../download_KAtree.py -l cs -c video
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get exercises for course $course"
    exit 1
  fi
  ../download_KAtree.py -l cs -c exercise
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get exercises for course $course"
    exit 1
  fi
fi

../ka_content_linking.py -a -c video 2>error.log
if [[ $? -ne 0 ]];then
  echo "ERROR: Could not print videos"
  exit 1
fi

../ka_content_linking.py -a -c exercise 2>>error.log
if [[ $? -ne 0 ]];then
  echo "ERROR: Could not print exercises"
  exit 1
fi

if [[ $SYNC != "true" ]];then
  exit 0
fi

# Copy all json files to the server
SRV="/srv/khanovaskola.cz/production/www/ppuc/"

# Temporary hack, we should rename these in RVP admin
mv ka_basic_geo_exercise.json ka_basic_geometry_exercise.json
mv ka_basic_geo_video.json ka_basic_geometry_video.json
mv ka_pre_algebra_exercise.json ka_pre-algebra_exercise.json
mv ka_pre_algebra_video.json ka_pre-algebra_video.json

ls *json
mv *json $SRV
