#!/bin/bash

# TODO: Download latest CS-KA tree for exercises and videos

courses=('cosmology-and-astronomy' 'early-math' 'arithmetic' \
  'trigonometry' 'basic-geo' 'pre-algebra' 'algebra-basics' 'music')


# TODO: Use these iterations in Python, will be much faster, can load tree only once per content type
# Need to refactor the python script first
for s in ${courses[@]}
do
  ../ka_content_linking.py -s $s -c video
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get videos for subject $s"
    exit 1
  fi
  ../ka_content_linking.py -s $s -c exercise
  if [[ $? -ne 0 ]];then
    echo "ERROR: Could not get exercises for subject $s"
    exit 1
  fi
done

# Copy all json files to the server
SRV="/srv/khanovaskola.cz/production/www/ppuc/"

# Temporary hack, we should rename these in RVP admin
mv ka_basic_geo_exercise.json ka_basic_geometry_exercise.json
mv ka_basic_geo_video.json ka_basic_geometry_video.json
mv ka_pre_algebra_exercise.json ka_pre-algebra_exercise.json
mv ka_pre_algebra_video.json ka_pre-algebra_video.json

ls *json
mv *json $SRV
