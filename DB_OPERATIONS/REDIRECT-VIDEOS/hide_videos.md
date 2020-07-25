### Useful SQL commands

SQL command to hide all videos inside blocks that have ka_url set

```sql
with T AS (
  SELECT ct.id, ct.title, ct.hidden
  FROM "contents" AS ct
  JOIN "content_block_bridges" AS cbb ON ct.id = cbb.content_id
  JOIN blocks AS bl ON bl.id = cbb.block_id
  WHERE ct.type = 'video' AND ct.hidden = 'f' AND ((bl.ka_url IS NOT NULL AND bl.ka_url != ''))
)
UPDATE contents AS ct
SET hidden = 't'
FROM T
WHERE ct.id = T.id;
```


# Hide videos from a specific block
```sql
WITH T AS (
SELECT ct.id, ct.title, ct.hidden, bl.title "Block title"
FROM "contents" AS ct
INNER JOIN "content_block_bridges" AS cbb ON cbb.content_id = ct.id
INNER JOIN "blocks" AS bl ON bl.id = cbb.block_id
WHERE bl.id = 96
)
UPDATE contents AS ct
SET hidden = 't'
FROM T
WHERE T.id = ct.id
```


# List all visible KS videos, together with block
# (contains duplicate videos)
```sql
SELECT ct.id, ct.title, ct.youtube_id, ct.youtube_id_original, ct.duration, ct.hidden, bl.id "Block ID", bl.title "Block title"
FROM "contents" AS ct
INNER JOIN "content_block_bridges" AS cbb ON cbb.content_id = ct.id
INNER JOIN "blocks" AS bl ON bl.id = cbb.block_id
WHERE (ct.ka_url = '' OR ct.ka_url IS NULL) AND ct.hidden = 'f'
ORDER BY bl.title
```
