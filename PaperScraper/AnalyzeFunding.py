import re
import pickle
import ast
import collections
import pandas as pd

import matplotlib.pyplot as plt

from ManageDocs import *

nsf_grant_types = ["iis", "cns", "ccf", "iia", "efri"]  # TODO expand list?
nsf_grant_re = r"(?:(?:NSF-)?([A-Z]{2,4}|Bigdata)(?:-| |:)? ?)?#?([0-9]{2}-?[0-9]{5})|([0-9]{6}(?: |_)[0-9]{6})"
funded_by_nsf_1 = r"((?:NSF|National Science Foundation|National Science Foundation through|National Science Foundation under\
                    |NSF through|NSF under) (?:(?:g|G)rants?|(?:A|a)wards?)(?:,?) ?(.{2,100}?)(?:,|\.))"
funded_by_nsf_2 = r"(NSF ({},? ?)*(?: and ?)?({}))".format(nsf_grant_re, nsf_grant_re)
# print(funded_by_nsf_2)
# quit()
funding_keywords = [
    funded_by_nsf_1,
    funded_by_nsf_2,
    r"((?:supported|funded) by ?(.{2,100}?)\.)",
]
# papers = get_all_papers(text_substr_len=None)
# outfile = open('papers.p','wb')
# pickle.dump(papers,outfile)
# outfile.close()

infile = open("papers.p", "rb")
papers = pickle.load(infile)
infile.close()
print("{} papers loaded".format(len(papers)))

paper_to_funding = {}
paper_to_nsf = collections.defaultdict(list)

for idx, paper in enumerate(papers):
    text = paper.paper_text
    for idx, regex in enumerate(funding_keywords):
        sources = re.findall(regex, text)
        if sources and idx != len(funding_keywords) - 1:  # last is catchall
            paper_to_funding[(paper.conference, paper.unique_id)] = sources
        elif sources:
            if "NSF" in sources[0]:
                print(sources)
            break

with open("../Data/AI_Conferences/nsf_funding.csv", "w") as funding_csv:
    writer = csv.writer(funding_csv)
    header = ["conference", "unique_id", "grant ID", "full funding string"]
    writer.writerow(header)
    for idx, (k, v) in enumerate(paper_to_funding.items()):
        res = re.findall(nsf_grant_re, v[0][0])
        # res = filter(lambda x: x != '', res)
        row = [k[0], k[1]]
        if res:
            res = res[0]
            res = [x for x in res if x != ""]
            # print(res)
            # print(str(res))
            row += [str(res)]  # TODO
            row += [v[0][0]]
        else:
            # row += v[0][0]
            print(v[0][0])
        writer.writerow(row)

paper_to_obj = get_paper_to_obj(papers)
id_to_count = collections.defaultdict(int)
id_to_paper = collections.defaultdict(set)
with open("../Data/AI_Conferences/nsf_funding.csv", "r") as funding_csv:
    csv_reader = csv.reader(funding_csv, delimiter=",")
    next(csv_reader)
    for line in csv_reader:
        conf = line[0]
        unique_id = line[1]
        if len(line) < 3:
            continue  # did not have grant specifics
        funding_str = line[2]
        for item in ast.literal_eval(funding_str):
            item = item.replace("-", "")
            if not item.isnumeric():
                id_to_count[item] += 1
                id_to_paper[item].add(paper_to_obj[conf, unique_id])
# print(id_to_count)

top_ten = sorted(id_to_count.items(), key=lambda item: -item[1])

with open("../Data/AI_Conferences/nsf_id_to_paper.csv", "w") as funding_csv:
    writer = csv.writer(funding_csv)
    header = ["grant_id"]
    writer.writerow(header)
    for (g_id, count) in top_ten:
        t_papers = id_to_paper[g_id]
        row = [g_id]
        row += [p.title for p in t_papers]
        writer.writerow(row)

top_ten = top_ten[:10]
plt.figure(figsize=(12, 8))
keys = [x[0] for x in top_ten]
vals = [x[1] for x in top_ten]
freq_series = pd.Series.from_array(vals)
ax = freq_series.plot(kind="bar")
plt.bar(range(len(vals)), vals, align="center")
plt.xticks(range(len(keys)), ["" for x in keys], rotation=45)

rects = ax.patches
for rect, label in zip(rects, keys):
    height = rect.get_height()
    ax.text(
        rect.get_x() + rect.get_width() / 2,
        height + 1,
        label,
        ha="center",
        va="bottom",
        rotation=60,
    )

plt.show()

inst_to_type = get_inst_to_inst_type()
paper_to_inst = get_paper_to_inst()
inst_to_count = collections.defaultdict(int)
with open("../Data/AI_Conferences/nsf_funding.csv", "r") as funding_csv:
    csv_reader = csv.reader(funding_csv, delimiter=",")
    next(csv_reader)
    for line in csv_reader:
        conf = line[0]
        unique_id = line[1]
        try:
            ppr = paper_to_obj[conf, unique_id]
            insts = paper_to_inst[(conf, unique_id)]
        except:
            print("Cannot find {}".format((conf, unique_id)))
            continue
        for inst in insts:
            if inst not in inst_to_type:
                continue
            if inst_to_type[inst] != "Academia":
                continue
            inst_to_count[inst] += 1

top_ten = sorted(inst_to_count.items(), key=lambda item: -item[1])
top_ten = top_ten[:20]
plt.figure(figsize=(12, 8))
keys = [x[0] for x in top_ten]
vals = [x[1] for x in top_ten]
freq_series = pd.Series.from_array(vals)
ax = freq_series.plot(kind="bar")
plt.bar(range(len(vals)), vals, align="center")
plt.xticks(range(len(keys)), ["" for x in keys], rotation=45)
rects = ax.patches
for rect, label in zip(rects, keys):
    height = rect.get_height()
    ax.text(
        rect.get_x() + rect.get_width() / 2,
        height + 1,
        label,
        ha="center",
        va="bottom",
        rotation=60,
    )
plt.show()

years = [2013, 2014, 2015, 2016, 2017, 2018, 2019]
nsf_per_year = [0 for x in years]
for paper, sources in paper_to_funding.items():
    # if 'NSF' in sources[0]:
    ppr = paper_to_obj[paper]
    year = ppr.year
    nsf_per_year[years.index(int(year))] += 1

total_per_year = [0 for x in years]
for p in papers:
    total_per_year[years.index(int(p.year))] += 1

plt.plot(years[:-1], nsf_per_year[:-1])
plt.plot(years[:-1], total_per_year[:-1])
plt.title("NSF funding for papers per year, 2013-2018")
plt.show()
