#!/usr/bin/awk -f

# Use as:
# $ ./create_postgres_queries.awk mapped_ytids_in_two_columns.dat

BEGIN{}
{
if (NF < 1 && NF > 2) {
  next
}
# Allow comments #
if ($1 == "#") {
  next
}

original_youtube_id=$1
YTID=original_youtube_id
print "UPDATE contents SET hidden = 't' WHERE youtube_id = '"YTID"' OR youtube_id_original = '"YTID"';"

translated_youtube_id=$2
if (translated_youtube_id != "" && translated_youtube_id != original_youtube_id) {
  YTID=translated_youtube_id
  print "UPDATE contents SET hidden = 't' WHERE youtube_id = '"YTID"' OR youtube_id_original = '"YTID"';"
}

}
END{}
