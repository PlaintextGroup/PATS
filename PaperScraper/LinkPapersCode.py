import os
import re
import csv
import sys
import json
import codecs
import requests
import collections
import urllib.parse
from time import sleep
from bs4 import BeautifulSoup

title_to_id = {}
title_to_code_urls = {}  # collections.defaultdict(list)
title_to_conference = {}
csv.field_size_limit(sys.maxsize)  # cannot read papers otherwise

sorted_files = sorted(os.listdir("../Data/AI_Conferences/"))
for folder_name in sorted_files:
    if not os.path.isdir("../Data/AI_Conferences/" + folder_name):
        continue
    print(folder_name)
    for fname in os.listdir("../Data/AI_Conferences/{}".format(folder_name)):
        if not fname.endswith("csv"):
            continue
        with open(
            "../Data/AI_Conferences/{}/{}".format(folder_name, fname), newline=""
        ) as csv_file:
            print(fname, len(title_to_code_urls))
            csv_reader = csv.reader(csv_file, delimiter=",")
            next(csv_reader)  # skip header
            try:
                for idx, row in enumerate(csv_reader):
                    title = row[2]
                    unique_id = row[0]
                    title_to_id[title] = unique_id  # TODO
                    title_to_code_urls[title] = list()
                    title_to_conference[title] = fname[:-8]
            except Exception as e:
                print("Failed on [{}]".format(fname))
                print("\t {}".format(e))

print("Searching papers with code")
with open("./lookup_tables/links-between-papers-and-code.json", "r") as json_file:
    paper_to_code = json.load(json_file)
    print("Loaded json")
    for paper in paper_to_code:
        title = paper["paper_title"]
        if title.strip() in title_to_code_urls:
            title_to_code_urls[title].append(paper["repo_url"])

num_with_code = 0
with open("./lookup_tables/papers_to_code.csv", "w") as new_csv:
    writer = csv.writer(new_csv)
    header = ["conference", "unique_id", "title", "code_urls"]
    writer.writerow(header)
    num_per_conference = collections.defaultdict(int)
    for title, repos in title_to_code_urls.items():
        if len(repos) > 0:
            conference = title_to_conference[title]
            unique_id = title_to_id[title]
            row = [conference, unique_id, title, repos]
            writer.writerow(row)
            num_with_code += 1
            num_per_conference[title_to_conference[title]] += 1

print("Found {} with code".format(num_with_code))
print(num_per_conference)
