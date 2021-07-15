import re
import pickle
import collections
import pandas as pd

import matplotlib.pyplot as plt

from ManageDocs import *

# If True, will regenerate entire citation graph among papers
CREATE_GRAPH = False

infile = open("papers.p", "rb")
papers = pickle.load(infile)
infile.close()

ppr_to_inst = get_paper_to_inst()
inst_to_type = get_inst_to_inst_type()

year_dict = {2013: 0, 2014: 1, 2015: 2, 2016: 3, 2017: 4, 2018: 5, 2019: 6}
years = [0] * 7

us_os = [0] * 7
cn_os = [0] * 7
all_os = [0] * 7

year_range = range(2013, 2020)
id_to_code = get_id_to_code_url()
inst_to_country = get_inst_to_country()

num_to_num = collections.defaultdict(int)
total_per_year = {str(x): 0 for x in year_range}
num_0 = 0

all_countries = {}

for p in papers:
    p_id = (p.conference, p.unique_id)
    if p_id not in ppr_to_inst:
        print(p_id, p.title, p.pdf_url)
        continue
    insts = ppr_to_inst[p_id]
    # has_other = False
    # has_govt = False
    # for inst in insts:
    #     i_type = inst_to_type[inst.strip()]
    #     # print(i_type)
    #     if i_type == 'Government': has_govt = True
    #     if i_type == 'Academia': has_other = True
    # if has_other and has_govt:
    if len(insts) == 0:
        num_0 += 1
    has_us = False
    has_cn = False
    idx = year_dict[int(p.year)]
    for inst in insts:
        if inst not in inst_to_country:
            print("{} not in inst_to_country".format(inst))
            continue
        c = inst_to_country[inst]

        if c == "US":
            has_us = True
        if c == "China":
            has_cn = True
        # all countries
        if c not in all_countries:
            all_countries[c] = [0] * 7
        all_countries[c][idx] += 1
    # if p_id in id_to_code:
    if has_us:
        us_os[idx] += 1
    if has_cn:
        cn_os[idx] += 1

    inst_set = set()
    for inst in insts:
        if inst not in inst_to_country:
            print("{} not in inst_to_country".format(inst))
            continue
        c = inst_to_country[inst]
        inst_set.add(c)
    num_to_num[len(inst_set)] += 1

    if p_id in id_to_code:
        idx = year_dict[int(p.year)]
        years[idx] += 1
    total_per_year[p.year] += 1
print(num_0, len(papers))
print(years)
if False:
    plt.title("Number of papers per year by each country")
    leg = []
    for c_key, counts in all_countries.items():
        # if c_key == 'US': continue # ignore USA
        if counts[-1] < 200:
            continue
        plt.plot(year_range[:-1], all_countries[c_key][:-1])
        leg.append(c_key)
    plt.legend(leg)
    # plt.legend(['US', 'China'])
elif False:
    cn_cv_yearly = [0] * 7
    cn_non_cv_yearly = [0] * 7
    for paper in papers:
        p_id = (paper.conference, paper.unique_id)
        idx = year_dict[int(paper.year)]
        if p_id not in ppr_to_inst:
            print(p_id, paper.title, paper.pdf_url, "no inst")
            quit()
        insts = set(ppr_to_inst[p_id])
        has_cn = False
        for inst in insts:
            if inst not in inst_to_country:
                print("{} not in inst_to_country {}".format(inst, paper.pdf_url))
                # print(insts)
                continue
                # quit()
            c = inst_to_country[inst]
            if c == "China":
                has_cn = True
                break
        if has_cn:
            conf = paper.conference
            # print(conf)
            if conf == "CVPR":  # or conf == 'ECCV':
                cn_cv_yearly[idx] += 1
            # elif conf == 'neurips' or conf == 'icml' or conf == 'aaai' or conf == 'iclr':
            else:
                if int(paper.year) == 2013:
                    print("\t" + paper.title)
                cn_non_cv_yearly[idx] += 1
    plt.title("China growth in cv and non cv conferences")
    # plt.plot(year_range[:-1], cn_cv_yearly[:-1])
    # plt.plot(year_range[:-1], cn_non_cv_yearly[:-1])
    plt.plot(year_range, cn_cv_yearly)
    plt.plot(year_range, cn_non_cv_yearly)
    print(year_range)

    def l_to_s(l):
        return str(l)[1:-1]

    print(l_to_s(cn_cv_yearly))
    print(l_to_s(cn_non_cv_yearly))
    plt.legend(["CV (cvpr)", "non-CV (icml,aaai,iclr)"])

elif False:
    cur_inst = "SenseTime Group Ltd."
    yearly_count = [0] * 7
    for paper in papers:
        if paper.conference == "ICCV":  # TODO
            continue
        p_id = (paper.conference, paper.unique_id)
        if p_id not in ppr_to_inst:
            print(p_id, paper.title, paper.pdf_url, "no inst")
            continue
        insts = set(ppr_to_inst[p_id])
        idx = year_dict[int(paper.year)]
        if cur_inst in insts:
            # print(p_id, paper.title, insts, paper.pdf_url)
            # print(paper.year)
            yearly_count[idx] += 1
    plt.title("Number of papers per year by {}".format(cur_inst))
    plt.plot(year_range[:-1], yearly_count[:-1])

elif False:
    tot_us_cn = 0
    tot_cn_cn = 0
    chinese_names = get_chinese_name_list()
    for paper in papers:
        p_id = (paper.conference, paper.unique_id)
        if p_id not in ppr_to_inst:
            print(p_id, paper.title, paper.pdf_url, "hi")
            continue
        insts = ppr_to_inst[p_id]
        only_us = True
        only_cn = True
        for inst in insts:
            if inst not in inst_to_country:
                print("{} not in inst_to_country".format(inst))
                continue
            c = inst_to_country[inst]
            if c != "US":
                only_us = False
            if c != "China":
                only_cn = False
        if not only_cn and not only_us:
            continue  # skip this paper
        # if only_cn:
        #     print(paper.title)
        authors = paper.authors
        found_chinese = False
        for author in authors:
            last_name = author.split(" ")[-1]
            for aliases in chinese_names:
                if not found_chinese:
                    for alias in aliases:
                        if last_name == alias:
                            found_chinese = True
                            break
            if found_chinese:
                break
        # if found_chinese:
        #     print(authors)
        if not found_chinese:
            continue
        if only_us:
            tot_us_cn += 1
        if only_cn:
            tot_cn_cn += 1
    print(tot_us_cn)
    print(tot_cn_cn)
    plt.bar(range(2), [tot_us_cn, tot_cn_cn], align="center")
    plt.xticks(
        range(2),
        [
            "Papers with one Chinese coauthor\npublished by US inst.",
            "Papers with one Chinese coauthor\npublished by Cn. inst.",
        ],
        rotation=0,
    )

elif False:
    inst_to_type = get_inst_to_inst_type()
    conf_to_yearly = collections.defaultdict(dict)
    yrset = set()
    for paper in papers:
        p_id = (paper.conference, paper.unique_id)
        yr = int(paper.year)
        yrset.add(yr)
        if p_id not in ppr_to_inst:
            print(p_id, paper.title, paper.pdf_url, "hi")
            continue
        if paper.conference not in conf_to_yearly:
            conf_to_yearly[paper.conference] = {yr: 0 for yr in year_dict.keys()}
        conf_to_yearly[paper.conference][int(paper.year)] += 1
    for k, v in conf_to_yearly.items():
        cur_d = v
        l2 = "{}; {}; {}; {}; {}; {}; {}".format(
            cur_d[2013],
            cur_d[2014],
            cur_d[2015],
            cur_d[2016],
            cur_d[2017],
            cur_d[2018],
            cur_d[2019],
        )
        print("{}; {}; {}".format(k, sum([y_num for y_num in cur_d.values()]), l2))
    # print(top_cn)
    print(yrset)

# python AnalyzeCitations.py
# python AnalyzeFunding.py

elif True:
    inst_to_type = get_inst_to_inst_type()
    all_i = set()
    print()
    for paper in papers:
        p_id = (paper.conference, paper.unique_id)
        insts = ppr_to_inst[p_id]
        has_us = False
        has_cn = False
        yr = int(paper.year)
        if yr < 2017:
            continue
        if not "health" in paper.paper_text or not "disease" in paper.paper_text:
            continue
        for inst in insts:
            if inst not in inst_to_country:
                # print('{} not in inst_to_country'.format(inst))
                continue
            if inst not in inst_to_type:
                # print('{} not in inst_to_type'.format(inst))
                continue
            i_type = inst_to_type[inst]
            if i_type != "Academia":
                continue
            all_i.add(paper.conference)
            # print(all_i)
            c = inst_to_country[inst]
            # print(inst_to_type[inst])
            if c == "US":
                has_us = True
            if c == "China":
                has_cn = True
        if has_cn and has_us:
            print("{}; {}; {}".format(p_id, paper.title, paper.pdf_url))

elif False:
    inst_to_type = get_inst_to_inst_type()
    inst_to_count = collections.defaultdict(float)
    inst_to_yearly = collections.defaultdict(dict)
    yrset = set()
    for paper in papers:
        p_id = (paper.conference, paper.unique_id)
        # if (paper.conference != 'CVPR'): continue
        yr = int(paper.year)
        # print(paper.year)
        yrset.add(yr)
        if p_id not in ppr_to_inst:
            print(p_id, paper.title, paper.pdf_url, "hi")
            continue
        insts = ppr_to_inst[p_id]
        for inst in insts:
            inst_to_count[inst] += 1
            if inst not in inst_to_yearly:
                inst_to_yearly[inst] = {yr: 0 for yr in year_dict.keys()}
            inst_to_yearly[inst][int(paper.year)] += 1
    top_institutions = sorted(inst_to_count.items(), key=lambda item: -item[1])
    top_us = []
    top_cn = []
    for tup in top_institutions:
        (inst, count) = tup
        if inst not in inst_to_country:
            print("{} not in inst_to_country".format(inst))
            continue
        c = inst_to_country[inst]
        # if c == 'US' and len(top_us) < 10:
        # if len(top_us) < 20:
        tup = (tup[0], tup[1], c)
        top_us.append(tup)
        # elif c == 'China' and len(top_cn) < 10:
        #     top_cn.append(tup)
    print(top_us)
    for idx, tup in enumerate(top_us):
        # print(idx+1, tup[0], tup[1])
        l1 = "{}; {}; {}".format(tup[0], tup[2], tup[1])
        # l2 = '{}, {}, {}, {}, {}, {}, {}'.format([[yr] for yr in year_dict.keys()])
        l2 = inst_to_yearly[tup[0]]
        cur_d = inst_to_yearly[tup[0]]
        l2 = "{}; {}; {}; {}; {}; {}; {}".format(
            cur_d[2013],
            cur_d[2014],
            cur_d[2015],
            cur_d[2016],
            cur_d[2017],
            cur_d[2018],
            cur_d[2019],
        )
        print("{}; {}".format(l1, l2))
    # print(top_cn)
    print(yrset)

elif False:
    plt.title("Number of papers per year by US and China")
    plt.plot(year_range[:-1], us_os[:-1])
    plt.plot(year_range[:-1], cn_os[:-1])
    plt.legend(["US", "China"])
elif False:
    print(num_to_num)
    num_to_num.pop(0, None)
    keys = [x[0] for x in num_to_num.items()]
    vals = [x[1] for x in num_to_num.items()]
    freq_series = pd.Series.from_array(vals)
    ax = freq_series.plot(kind="bar")
    plt.bar(range(len(vals)), vals, align="center")
    plt.title("Number of papers co-authored by institutions from n countries")
    plt.xticks(range(len(keys)), keys, rotation=0)
elif False:
    plt.title("Pct open-source per year")
    for idx, val in enumerate(years):
        year = year_range[idx]  # TODO check
        num_year = total_per_year[str(year)]
        years[idx] /= num_year

    plt.plot(year_range[:-1], years[:-1])

plt.show()


# if CREATE_GRAPH:
#     for ppr in papers:
#         ppr.paper_text = ppr.paper_text[-5000:]

#     paper_titles = {}
#     for p in papers:
#         paper_titles[p.title] = p

#     print(len(paper_titles))

#     paper_to_linked_papers = collections.defaultdict(set)

#     for idx,p in enumerate(papers):
#         text = p.paper_text
#         for t in paper_titles:
#             if t == p.title: continue
#             if t in text:
#                 link = paper_titles[t]
#                 # paper_to_linked_papers[(p.conference,p.unique_id)].add((link.conference,link.unique_id)) # TODO refresh next time
#                 paper_to_linked_papers[(p.conference,p.unique_id)].add(link) # TODO use primary key
#         if idx % 10 == 0:
#             print('{} / {}'.format(idx,len(papers)))
#     outfile = open('citations.p','wb')
#     pickle.dump(paper_to_linked_papers,outfile)
#     outfile.close()
# else:
#     paper_to_obj = get_paper_to_obj(papers)
#     infile = open('citations.p','rb')
#     paper_to_linked_papers = pickle.load(infile)
#     infile.close()
#     print('Loaded')
#     top_cited = sorted(paper_to_linked_papers, key=lambda k: len(paper_to_linked_papers[k]), reverse=True)
#     for t in top_cited[:10]:
#         print(paper_to_obj[t].title, paper_to_obj[t].pdf_url)
#         for c in paper_to_linked_papers[t]:
#             print('\t{}, {}'.format(c.title, c.pdf_url))
