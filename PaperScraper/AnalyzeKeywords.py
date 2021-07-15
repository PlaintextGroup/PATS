import copy
import math
import random
import pickle
import operator
import collections

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ManageDocs import *

# write_paper_to_insts()
# quit()

# all_neurips = get_all_papers()
infile = open("papers.p", "rb")
all_neurips = pickle.load(infile)
infile.close()
# for ppr in all_neurips:
#     ppr.paper_text = ppr.paper_text[:1000]

paper_to_inst = get_paper_to_inst()
name_to_affil = get_author_affil()

years = range(2013, 2020)  # 2013-2019 (inclusive)

# all_keywords = ['imagenet','transfer learning','gpu','quantum','adversarial','autonomous vehicle','healthcare',
#                 'facial recognition','drone','generative adversarial network','robotic','explainable','deep fake','alexnet','convolutional']
all_keywords = [
    "imagenet",
    "transfer learning",
    "gpu",
    "quantum",
    "adversarial",
    "explainable",
    "convolutional",
    "generative adversarial network",
    "facial recognition",
]
all_keywords = sorted(all_keywords)

dual_use_keywords = ["robot", "autonomous", "adversarial training"]
dual_use_keywords = sorted(dual_use_keywords)

# creates a dict from year to number of papers for the given set of papers, topic, and country
def assess_interest(
    papers,
    topic,
    country,
    paper_to_inst=get_paper_to_inst(),
    inst_to_country=get_inst_to_country(),
    use_text=True,
    only_open_source=False,
):
    country = country.lower()
    topic = topic.lower()
    num_year = collections.defaultdict(int)
    id_to_code = get_id_to_code_url()
    paper_ids = set()
    if topic.endswith("-open"):
        topic = topic.split("-open")[0]
    for paper in papers:
        # print(len(paper.paper_text))
        if only_open_source:
            if (paper.conference, paper.unique_id) not in id_to_code:
                continue
        if country != "":
            paper_insts = paper_to_inst[(paper.conference, paper.unique_id)]
            has_country = False
            for inst in paper_insts:
                try:
                    inst_country = inst_to_country[inst]
                except:
                    print("Failed to get country for [{}]".format(inst))
                    continue
                if inst_country.lower() == country:
                    has_country = True
                    break
            if not has_country:
                continue
        if topic in paper.abstract.lower() or (
            topic in paper.paper_text.lower() and use_text
        ):  # TODO lowercase?
            # print(paper.title)
            num_year[int(paper.year)] += 1  # TODO decide whether make year an int
            paper_ids.add((paper.conference, paper.unique_id))
    return num_year, paper_ids


def create_growth_graph(
    list_of_dicts, list_of_labels, truncate_2019=True, country=None
):
    for idx, year_dict in enumerate(list_of_dicts):
        year_dict = year_dict[0]
        new_x = copy.deepcopy(years)
        print(year_dict)
        new_y = [year_dict[x] if x in year_dict else 0 for x in years]
        if truncate_2019:
            new_x = new_x[:-1]
            new_y = new_y[:-1]
        print(new_x, new_y)
        plt.plot(new_x, new_y, label=list_of_labels[idx])
    country_keyword = "" if country is None else "from {} ".format(country)
    plt.title("AI papers {}published with keywords".format(country_keyword))
    plt.legend(loc="best")
    plt.show()


def make_interest_graph(countries, keywords, width=0.3):
    open_keywords = [x + "-open" for x in keywords]
    keywords = keywords + open_keywords
    keywords = sorted(keywords)
    df = pd.DataFrame(columns=countries)
    for idx, country in enumerate(countries):
        keyword_to_interest = collections.defaultdict(int)
        for keyword in keywords:
            if keyword.endswith("-open"):
                country_only, _ = assess_interest(
                    all_neurips, keyword, country, use_text=True, only_open_source=True
                )
                interest, _ = assess_interest(
                    all_neurips, "", country, use_text=True, only_open_source=True
                )
                country_all = sum(list(interest.values()))
            else:
                country_only, _ = assess_interest(
                    all_neurips, keyword, country, use_text=True
                )
                all_interest, _ = assess_interest(
                    all_neurips, keyword, "", use_text=True
                )  # country = '' means all countries
            sum_1 = sum([v for k, v in country_only.items()])
            sum_2 = sum([v for k, v in all_interest.items()])
            if sum_2 == 0:
                print("Interest 0 for {} :'( for {}".format(keyword, country))
                # continue
                frac = 0.0  # TODO! assess better
            else:
                # frac = sum_1 / sum_2
                interest_1, _ = assess_interest(all_neurips, "", country, use_text=True)
                country_all = sum(list(interest_1.values()))
                interest_2, _ = assess_interest(all_neurips, "", "", use_text=True)
                all_papers = sum(list(interest_2.values()))

                # experiment - fraction_interested_in_country / fraction_interested_total
                frac_1 = sum_1 / country_all
                frac_2 = sum_2 / all_papers
                # frac = frac_1 / frac_2
                frac = frac_1
            keyword_to_interest[keyword] = frac

        interest_sorted = [keyword_to_interest[x] for x in keywords]
        df[country] = interest_sorted
    ind = np.arange(len(df))
    for idx, country in enumerate(countries):
        plt.barh(
            ind - width * idx / 2.0, df[country], width, align="center", label=country
        )

    plt.yticks(range(len(keyword_to_interest)), list(keyword_to_interest.keys()))
    plt.subplots_adjust(left=0.4)
    plt.title("Relative paper share by keyword")
    plt.legend(loc="best")
    plt.show()


country = ""
topics = ["tensorflow", "pytorch"]
# topics = ['']
results = [
    assess_interest(all_neurips, x, country, use_text=True, only_open_source=True)
    for x in topics
]
# print(results)
create_growth_graph(results, topics, country=country, truncate_2019=False)

# countries = ['US','China','France']
# make_interest_graph(countries, [''])

# results = [assess_interest(all_neurips, x, '', use_text=True, only_open_source=True) for x in dual_use_keywords]
# print(results)
