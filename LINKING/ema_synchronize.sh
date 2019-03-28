#!/bin/bash

# Only for debuggind
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

SYNC=true
DOWNLOAD=true

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

courses=('cosmology-and-astronomy' 'early-math' 'arithmetic' \
  'trigonometry' 'basic-geo' 'pre-algebra' 'algebra-basics' 'music')

# TODO: Use these iterations in Python, will be much faster, can load tree only once per content type
# Need to refactor the python script first
for course in ${courses[@]}
do
  ../ka_content_linking.py -s $course -c video
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get videos for course $course"
    exit 1
  fi
#  compare_reference $course "video"
  ../ka_content_linking.py -s $course -c exercise
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get exercises for course $course"
    exit 1
  fi
#  compare_reference $course "exercise"
done

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
