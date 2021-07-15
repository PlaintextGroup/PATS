import re
import nltk
import pickle
import random
import collections
import numpy as np
import pandas as pd

from ManageDocs import *

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

import matplotlib.pyplot as plt

infile = open("papers.p", "rb")
papers = pickle.load(infile)
infile.close()

papers = get_papers_without_references(papers)

categories = get_category_dict()
# paper_to_kws = np.zeros((len(papers),len(categories),50))
paper_to_cats = collections.defaultdict(set)
paper_to_kws = collections.defaultdict(set)

for idx_1, paper in enumerate(papers):
    abstract = paper.abstract
    for idx_2, (cat, cat_kws) in enumerate(categories.items()):
        has_cat = False
        for idx_3, kw in enumerate(cat_kws):
            if has_cat:
                break
            # if kw.lower() in abstract.lower() + ' ' + paper.title.lower():
            full_str = abstract.lower() + " " + paper.title.lower()
            # print(kw)
            # reg = re.compile('\b{}\b'.format(kw.lower()))
            # print(reg)
            if re.search(r"\b{}\b".format(kw.lower()), full_str):
                # paper_to_kws[idx_1][idx_2][idx_3] = 1.0
                paper_to_cats[paper].add(cat)
                has_cat = True
                paper_to_kws[paper].add(kw)

# for p,i in paper_to_cats.items():
#     print(p,i)
# random.shuffle(papers)
papers = sorted(papers, key=lambda x: x.title)
for idx, p in enumerate(papers):
    if p not in paper_to_cats:
        print(p.title, p.pdf_url)
        if idx > 8000:
            break

print(
    "{} / {} = {}".format(
        len(paper_to_cats), len(papers), len(paper_to_cats) / len(papers)
    )
)

# p_to_dual = {}
# for idx,(p,i) in enumerate(paper_to_cats.items()):
#     row = [p.conference,p.unique_id,p.title,i]
#     p_dual_use = 0.0
#     for cat in i:
#         p_dual_use += categories[cat][0]
#     p_to_dual[p] = p_dual_use

# top_dual = sorted(p_to_dual.items(), key=lambda kv: -kv[1])
# for p in top_dual[:10]:
#     pap = p[0]
#     print(pap.title, pap.pdf_url, p[1], paper_to_cats[pap])

# quit()

with open("topics.csv", "w") as topics_csv:
    writer = csv.writer(topics_csv)
    header = ["conference", "unique_id", "title", "categories", "keywords", "PDF link"]
    writer.writerow(header)
    for idx, (p, i) in enumerate(paper_to_cats.items()):
        row = [p.conference, p.unique_id, p.title, i, paper_to_kws[p], p.pdf_url]
        writer.writerow(row)

cat_to_count = collections.defaultdict(int)
for idx, (p, i) in enumerate(paper_to_cats.items()):
    for c in i:
        cat_to_count[c] += 1

print(cat_to_count)
D = cat_to_count
plt.barh(range(len(D)), list(D.values()), align="center")
plt.yticks(range(len(D)), list(D.keys()))
plt.subplots_adjust(left=0.4)
plt.show()
