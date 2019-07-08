When we publish new content on Czech Khan Academy (cs.khanacademy.org),
we need to hide the overlapping videos at khanovaskola.cz

Here is a semi-automated process for doing so.

1. Get the list of Original YouTube IDs
This is a bit tricky, because the Public Khan API does not differentiate between listed and unlisted content. So we basically need to do this manually.

2. Map English videos to re-created videos
We want to have a list of both the original YouTube IDs and YTIDs of re-created videos, because both can be present at KŠ web. We do this via a script leveraging Khan API.
    ../../map_ytid_to_khandata.py -l cs -a translated_youtube_id original_ytids.dat > mapped_ytids.dat

3. Generate SQL queries
    ./create_postgres_queries.awk mapped_ytids.dat > mapped_ytids.sql

4. Enter PostgreSQL prompt
    sudo su - postgres

5. Connect to khanovaskola DB and Execute queries
    psql -d khanovaskola -f ABSOLUTE_PATH/mapped_ytids.sql

6. Hide entire video blocks, if necessary
This is done by editing a block via web interface at khanovaskola.cz/blok-editor

One might also wish to hide videos not from a list of YTIDs, but from specific blocks at KŠ.
See \*sql files in this folder for example SQL commands to do this.
(hint: You'll need block IDs)


TODO:
We should create a new DB attribute which would set noindex property for a video but still keep it in ElasticSearch index on KŠ so that users searching directly at khanovaskola.cz are not impacted.

MAYBE-TODO: Redirect such pages directly to cs.khanacademy.org
