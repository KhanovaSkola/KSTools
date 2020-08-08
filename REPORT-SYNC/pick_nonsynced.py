import sys

synced_ytids = set()
with open("all_synced.txt", "r") as f:
    for line in f:
        synced_ytids.add(line.strip())

with open("all.txt", "r") as f:
    for line in f:
        ytid = line.split("\t")[0].strip()
        if ytid not in synced_ytids:
            print(line.strip())
