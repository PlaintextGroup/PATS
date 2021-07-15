import config as cfg
import re
import pickle
import collections
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from manage_docs import *
from tqdm import tqdm
import os
import time
from os import path
import operator

print("=====================================")
print("        CONFIGURATION CHOSEN         ")
print("=====================================")

for field in cfg.citations:
    if cfg.citations[field]:
        print(field + ": " + str(cfg.citations[field]))

print(" ")
print("=====================================")
print("            LOADING FILES            ")
print("=====================================")
print("Starting Preprocessing....")
infile = open("papers2.p", "rb")
papers = pickle.load(infile)

infile.close()

ppr_to_inst = get_paper_to_inst()
inst_to_type = get_inst_to_inst_type()
# print(inst_to_type)

year_dict = {2013: 0, 2014: 1, 2015: 2, 2016: 3, 2017: 4, 2018: 5, 2019: 6}
years = [0] * 7

country_options = [
    "Australia",
    "Austria",
    "Belgium",
    "Brazil",
    "Canada",
    "Chile",
    "China",
    "Colombia",
    "Czechia",
    "Denmark",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hong Kong",
    "Hungary",
    "India",
    "Iran",
    "Ireland",
    "Israel",
    "Italy",
    "Japan",
    "Lebanon",
    "Luxembourg",
    "Netherlands",
    "New Zealand",
    "Norway",
    "Poland",
    "Portugal",
    "Qatar",
    "Russia",
    "Singapore",
    "South Korea",
    "Spain",
    "Sweden",
    "Switzerland",
    "Taiwan",
    "Turkey",
    "UAE",
    "UK",
    "US",
    "Ukraine",
    "Uruguay",
]

conference_options = ["aaai", "CVPR", "iclr", "icml", "neurips"]

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
unique_conf = []

papers_df = pd.DataFrame.from_records(p.to_dict() for p in papers)
inst_col = []
country_col = []
inst_type_col = []
code_col = []
unique_countries = set()

for p in tqdm(papers):
    inst_set = set()
    inst_type_set = set()
    conf = p.conference
    if conf not in unique_conf:
        unique_conf.append(conf)
    p_id = (p.conference, p.unique_id)
    if p_id not in ppr_to_inst:
        print(p_id, p.title, p.pdf_url)
        continue
    insts = ppr_to_inst[p_id]
    if len(insts) == 0:
        num_0 += 1
        insts = ["UnknownInstitution"]
        inst_set.add("UnknownCountry")
        inst_type_set.add("UnknownInstitutionType")

    inst_col.append(", ".join(set(insts)))
    has_us = False
    has_cn = False
    idx = year_dict[int(p.year)]
    for inst in insts:
        inst = inst.strip()
        if inst not in inst_to_country:
            if cfg.citations["verbose"]:
                print("{} not in inst_to_country".format(inst))
            continue
        if inst not in inst_to_type:
            if cfg.citations["verbose"]:
                print("{} not in inst_to_type".format(inst))

        c = inst_to_country[inst]
        inst_set.add(c)
        unique_countries.add(c)
        inst_type = inst_to_type[inst]
        inst_type_set.add(inst_type)

        if c == "US":
            has_us = True
        if c == "China":
            has_cn = True
        # all countries
        if c not in all_countries:
            all_countries[c] = [0] * 7
        all_countries[c][idx] += 1
    country_col.append(", ".join(sorted(inst_set)))  ## unique_countries?
    inst_type_col.append(", ".join(sorted(inst_type_set)))
    if has_us:
        us_os[idx] += 1
    if has_cn:
        cn_os[idx] += 1
    num_to_num[len(inst_set)] += 1

    if p_id in id_to_code:
        code_col.append(id_to_code[p_id])
        idx = year_dict[int(p.year)]
        years[idx] += 1
    else:
        code_col.append("NotOpenSource")
    total_per_year[p.year] += 1


def try_join(l):
    if type(l) == str:
        return l
    else:
        cleaned = []
        for author in l:
            author_sep = author.split(",")
            for sep in author_sep:
                sep = sep.strip()
                if len(sep) <= 2:
                    continue
                if sep[-1] == ",":
                    sep = sep[:-1]
                cleaned.append(sep)
        return ", ".join(map(str, cleaned))


papers_df["authors_string"] = [try_join(l) for l in papers_df["authors"]]

# 2730 unknown institutions
# print(num_0)

papers_df["Institution"] = inst_col
papers_df["Institution Type"] = inst_type_col
papers_df["Countries"] = country_col
papers_df["OpenSource"] = code_col

print(" ")
print("=====================================")
print("            FILTERING....            ")
print("=====================================")


# create dataframe for analysis
if cfg.citations["country_analyzed"]:
    papers_df = papers_df[
        papers_df["Countries"].str.contains("|".join(cfg.citations["country_analyzed"]))
    ]

if cfg.citations["years_analyzed"]:
    cfg.citations["years_analyzed"] = list(map(str, cfg.citations["years_analyzed"]))
    papers_df = papers_df[papers_df["year"].isin(cfg.citations["years_analyzed"])]

if cfg.citations["institution_analyzed"]:
    papers_df = papers_df[
        papers_df["Institution"].str.contains(
            "|".join(cfg.citations["institution_analyzed"])
        )
    ]

if cfg.citations["institution_type_analyzed"]:
    ## TODO ONLY WORKS FOR 1 RIGHT NOW
    if cfg.citations["institution_type_strict"]:
        papers_df = papers_df[
            papers_df["Institution Type"]
            == cfg.citations["institution_type_analyzed"][0]
        ]
    else:
        papers_df = papers_df[
            papers_df["Institution Type"].str.contains(
                "|".join(cfg.citations["institution_type_analyzed"])
            )
        ]

if cfg.citations["institution_type_dependent"]:
    final_filtered_df = pd.DataFrame(columns=papers_df.columns)
    if len(cfg.citations["country_analyzed"]) != len(
        cfg.citations["institution_type_analyzed"]
    ):
        print(
            "Please make sure that that for every country, you have also selected an institution type. The lengths should be equal."
        )
        print(
            "For example, if I select US and China as countries, I also need to specify Academia, Company"
        )
        print(
            "within the 'institution_type_analyzed' field if I want 1) academic papers from the US and 2) company papers from China."
        )
        print(
            "If where the academic and company paper origins do not matter (I want both from US and China), mark this field as 'False', "
        )
        print(
            "and put ['Company', 'Academia'] within the 'institution_type_analyzed' field instead."
        )
        exit()
    for i in range(len(cfg.citations["country_analyzed"])):
        country_filter = cfg.citations["country_analyzed"][i]
        institution_type_filter = cfg.citations["institution_type_analyzed"][i]

        ## TODO get aliases
        country_entries = []
        final_country_types = []
        for entry in inst_to_country:
            if entry in inst_to_country:
                if inst_to_country[entry] == country_filter:
                    country_entries.append(entry)
            else:
                continue
        for entry in country_entries:
            if entry in inst_to_type:
                if inst_to_type[entry] == institution_type_filter:
                    final_country_types.append(entry)
            else:
                continue

        filtered_df = papers_df[papers_df["Countries"].str.contains(country_filter)]
        filtered_df = filtered_df[
            filtered_df["Institution"].str.contains("|".join(final_country_types))
        ]
        final_filtered_df = final_filtered_df.append(filtered_df)

    papers_df = final_filtered_df


if cfg.citations["conferences_analyzed"]:
    for i in range(len(cfg.citations["conferences_analyzed"])):
        if cfg.citations["conferences_analyzed"][i] == "cvpr":
            cfg.citations["conferences_analyzed"][i] = cfg.citations[
                "conferences_analyzed"
            ][i].upper()

    papers_df = papers_df[
        papers_df["conference"].isin(cfg.citations["conferences_analyzed"])
    ]

if cfg.citations["keywords"]:
    contains = [
        papers_df["paper_text"].str.contains(word) for word in cfg.citations["keywords"]
    ]
    papers_df = papers_df[np.all(contains, axis=0)]
    for word in cfg.citations["keywords"]:
        count_mask = (
            papers_df["paper_text"].str.count(word)
            >= cfg.citations["min_keyword_count"]
        )
        papers_df = papers_df[count_mask]

if cfg.citations["only_chinese_coauthors"]:

    chinese_names = get_chinese_name_list()
    flattened_chinese_names = [item for sublist in chinese_names for item in sublist]
    flattened_chinese_names = [
        name for name in flattened_chinese_names if str(name) != "nan"
    ]
    papers_df = papers_df[papers_df["authors"].notna()]
    papers_df = papers_df[
        papers_df["authors"].str.contains("|".join(flattened_chinese_names), na=False)
    ]


# insts = list(papers_df.Institution)
# insts_set = set()
# for inst_str in insts:
#     inst_sep = inst_str.split(',')
#     for sep in inst_sep:
#         sep = sep.strip()
#         insts_set.add(sep)
print(" ")
print("=====================================")
print("                OUTPUT               ")
print("=====================================")


print("Final Titles: ")
print(papers_df.title)

# print("Final Institutions: ")
# print(papers_df.Institution)
# print("Final Countries: ")
# print(papers_df.Countries)
# papers_df = papers_df[count_mask]
# papers_df = papers_df[papers_df['paper_text'].count(cfg.citations["keywords"][0]) >= cfg.citations["min_keyword_count"]]
# for word in cfg.citations["keywords"]:
#     papers_df = papers_df[papers_df['paper_text'].count(word) >= cfg.citations["min_keyword_count"]]
# print(paper.paper_text.count(cfg.citations["keywords"]))
# print(papers_df.conference.unique())

if cfg.citations["verbose"]:
    print("Missing Institions: ", num_0)
    print("Papers Analyzed: ", papers_df.shape[0])
    # print("US OS: ", us_os)
    # print("US sum: ", sum(us_os))
    # print("China OS: ", cn_os)
    # print("China sum: ", sum(cn_os))

    # Verbose - prints out conference publications by year
    years_analyzed = (
        cfg.citations["years_analyzed"]
        if cfg.citations["years_analyzed"]
        else list(year_range)
    )
    conferences_analyzed = (
        cfg.citations["conferences_analyzed"]
        if cfg.citations["conferences_analyzed"]
        else ["aaai", "CVPR", "iclr", "icml", "neurips"]
    )
    print("Unique Conferences Analyzed: ", conferences_analyzed)
    print("Years Analyzed: ", years_analyzed)
    print("# of Papers by Year: ", years)
    plt.figure()
    plt.title(
        "Number of papers by conference- Conf: Keywords: "
        + str(cfg.citations["keywords"])
    )
    leg = []
    for conf in conferences_analyzed:
        conf_df = papers_df[papers_df["conference"].str.contains(conf)]
        conf_yearly = []
        for year in years_analyzed:
            conf_yearly.append(conf_df[conf_df["year"] == str(year)].shape[0])
        plt.plot(years_analyzed, conf_yearly)
        leg.append(conf)
    plt.legend(leg)

if cfg.citations["plot_data"]:
    if cfg.citations["verbose"]:
        print(all_countries.items())
    years_analyzed = (
        cfg.citations["years_analyzed"]
        if cfg.citations["years_analyzed"]
        else list(year_range)
    )
    conferences_analyzed = (
        cfg.citations["conferences_analyzed"]
        if cfg.citations["conferences_analyzed"]
        else conference_options
    )
    if cfg.citations["verbose"]:
        print("Years Analyzed: ", years_analyzed)
        print("Conferences Analyzed: ", conferences_analyzed)

    # COUNTRIES
    plt.figure()
    plt.title(
        "Number of papers per year by country- Conf: "
        + str(conferences_analyzed)
        + ", Keywords: "
        + str(cfg.citations["keywords"])
    )
    leg = []
    total_country = {}
    country_analyzed = (
        cfg.citations["country_analyzed"]
        if cfg.citations["country_analyzed"]
        else country_options
    )
    for country in country_analyzed:
        country_df = papers_df[papers_df["Countries"].str.contains(country)]
        country_yearly = []
        for year in years_analyzed:
            country_yearly.append(country_df[country_df["year"] == str(year)].shape[0])
        total_country[country] = (sum(country_yearly), country_yearly)

    final_country = {
        k: v
        for k, v in sorted(
            total_country.items(), key=lambda item: item[1], reverse=True
        )
    }

    print()
    print("Country output: ", final_country)
    print()

    data_list = list(final_country.items())
    num_plotted = (
        cfg.citations["n_plotted"]
        if len(cfg.citations["country_analyzed"]) == 0
        else len(cfg.citations["country_analyzed"])
    )
    for i in range(0, num_plotted):
        cur_country = data_list[i][0]
        entry = data_list[i][1][1]
        if cfg.citations["institution_type_dependent"]:
            plt.plot(
                years_analyzed,
                entry,
                label=str(cur_country)
                + " -- "
                + cfg.citations["institution_type_analyzed"][i],
            )
        else:
            plt.plot(years_analyzed, entry, label=str(cur_country))
        plt.legend()

    ## INSTITUTIONS
    plt.figure()
    plt.title(
        "Number of papers per year by Institution- Conf: "
        + str(conferences_analyzed)
        + ", Keywords: "
        + str(cfg.citations["keywords"])
    )
    insts = list(papers_df.Institution)
    insts_set = set()
    for inst_str in insts:
        inst_sep = inst_str.strip()
        inst_sep = inst_str.split(",")
        for sep in inst_sep:
            insts_set.add(sep)

    institutions_analyzed = (
        cfg.citations["institution_analyzed"]
        if cfg.citations["institution_analyzed"]
        else list(insts_set)
    )
    print(len(institutions_analyzed))
    total_inst = {}
    for cur_inst in institutions_analyzed:
        inst_df = papers_df[papers_df["Institution"].str.contains(cur_inst)]
        inst_papers_yearly = []
        for year in years_analyzed:
            inst_papers_yearly.append(inst_df[inst_df["year"] == str(year)].shape[0])
        cur_inst = (
            cur_inst.strip()
        )  # putting this here because it wasn't stripped correctly before plugging in from manage_docs
        if cur_inst not in total_inst:
            total_inst[cur_inst] = (sum(inst_papers_yearly), inst_papers_yearly)
        else:
            old_yearly = total_inst[cur_inst][1]  # list
            summed_list = [a + b for a, b in zip(inst_papers_yearly, old_yearly)]
            total_inst[cur_inst] = (sum(summed_list), summed_list)

    final_inst = {
        k: v
        for k, v in sorted(total_inst.items(), key=lambda item: item[1], reverse=True)
    }

    print()
    print("Institution output: ", final_inst)
    print()

    # only does it for 1 right now
    if cfg.citations["country_analyzed"] and cfg.citations["institution_type_analyzed"]:
        final_filter = {}
        for entry in final_inst:
            if entry in inst_to_type and entry in inst_to_country:
                if (
                    inst_to_type[entry] == cfg.citations["institution_type_analyzed"][0]
                    and inst_to_country[entry] == cfg.citations["country_analyzed"][0]
                ):
                    final_filter[entry] = final_inst[entry]

        final_filter2 = {
            k: v
            for k, v in sorted(
                final_filter.items(), key=lambda item: item[1], reverse=True
            )
        }

        print("Final filter ", final_filter2)

        final_inst = final_filter2

    # for k in list(final_inst):
    #     if len(k) <= 2: final_inst.pop(k)

    data_list = list(final_inst.items())
    num_plotted = (
        cfg.citations["n_plotted"]
        if len(cfg.citations["institution_analyzed"]) == 0
        else len(cfg.citations["institution_analyzed"])
    )
    if len(data_list) < num_plotted:
        num_plotted = len(data_list)
    for i in range(0, num_plotted):
        cur_inst = data_list[i][0]
        entry = data_list[i][1][1]
        plt.plot(years_analyzed, entry, label=str(cur_inst))
        plt.legend()

# ## TODO expand to other countries if possible. how did they get last name -- regular scraper?
# if cfg.citations["chinese_coauthor_analysis"]:
#     tot_us_cn = 0
#     tot_cn_cn = 0
#     chinese_names = get_chinese_name_list()
#     tot_us = 0
#     tot_cn = 0
#     tot_years = []
#     for paper in papers:
#         curr_year = int(paper.year)
#         if curr_year not in tot_years: tot_years.append(curr_year)
#         p_id = (paper.conference,paper.unique_id)
#         if p_id not in ppr_to_inst:
#             if cfg.citations["verbose"]: print(p_id, paper.title, paper.pdf_url, 'Institution not tagged')
#             continue
#         insts = ppr_to_inst[p_id]
#         only_us = True
#         only_cn = True
#         for inst in insts:
#             if inst not in inst_to_country:
#                 if cfg.citations["verbose"]: print('{} not in inst_to_country'.format(inst))
#                 continue
#             c = inst_to_country[inst]
#             # if c == 'US': tot_us += 1
#             # if c == 'China': tot_cn += 1
#             if c != 'US':
#                 only_us = False
#             if c != 'China':
#                 only_cn = False
#         if not only_cn and not only_us:
#             continue # skip this paper
#         # if only_cn:
#         #     print(paper.title)
#         authors = paper.authors
#         found_chinese = False
#         for author in authors:
#             last_name = author.split(' ')[-1]
#             for aliases in chinese_names:
#                 if not found_chinese:
#                     for alias in aliases:
#                         if last_name == alias:
#                             found_chinese = True
#                             break
#             if found_chinese:
#                 break
#         # if found_chinese:
#         #     print(authors)
#         if not found_chinese:
#             continue
#         if only_us:
#             tot_us_cn += 1
#         if only_cn:
#             tot_cn_cn += 1
#
#     plt.title('US and Chinese Institution and Coauthor relationships')
#     plt.bar(range(2), [tot_us_cn, tot_cn_cn], align='center')
#     plt.xticks(range(2), ['Papers with one Chinese coauthor\npublished by US inst.', 'Papers with one Chinese coauthor\npublished by Cn. inst.'], rotation=0)
#
#     if cfg.citations["verbose"]:
#         print("Years Analyzed: ", tot_years)
#         print("Total US Chinese: ", tot_us_cn)
#         print("Total Chinese Chinese: ", tot_cn_cn)


## TODO
if cfg.citations["analyze_coauthors"]:
    data = {}
    for row in papers_df.Institution:
        num = len(row.split(","))
        if num not in data:
            data[num] = 1
        else:
            data[num] += 1
    plt.figure()
    plt.bar(data.keys(), data.values())
    # if cfg.citations["verbose"]: print("Number of Institutions on a Paper", num_to_num)
    # num_to_num.pop(0, None)
    # keys = [x[0] for x in num_to_num.items()]
    # vals = [x[1] for x in num_to_num.items()]
    # freq_series = pd.Series(vals)
    # ax = freq_series.plot(kind='bar')
    # plt.bar(range(len(vals)), vals, align='center')
    plt.title("Number of papers co-authored by institutions from n countries")
    # plt.xticks(range(len(keys)), keys, rotation=0)

if cfg.citations["open_source"]:  # open source if there is an associated code URL
    plt.figure()
    plt.title("Open Source Papers by Year")
    years_analyzed = (
        cfg.citations["years_analyzed"]
        if cfg.citations["years_analyzed"]
        else list(year_range)
    )
    years_pcts = []
    for year in years_analyzed:
        yearly_df = papers_df[papers_df["year"] == str(year)]
        open_source = yearly_df[~(yearly_df["OpenSource"] == "NotOpenSource")].shape[0]
        # total_year = yearly_df.shape[0]
        # pct = open_source / total_year
        years_pcts.append(open_source)  # can be pct
    plt.plot(years_analyzed, years_pcts)


# TODO TO FIX EDGE CASES
if cfg.citations["top_authors"]:
    years_analyzed = (
        cfg.citations["years_analyzed"]
        if cfg.citations["years_analyzed"]
        else list(year_range)
    )
    total_authors = {}

    # extract authors
    author_list = list(papers_df.authors_string)
    # authors = [item for sublist in author_list for item in sublist]

    authors_set = set()
    for author in author_list:
        author_sep = author.split(",")
        for sep in author_sep:
            sep = sep.strip()
            authors_set.add(sep)

    uncleaned_authors = [
        "Stefano Soatto and Alessandro Chiuso                   |",
        "and Pierre Baldi                                  |",
        "Richard",
        "Andrea",
    ]

    for cur_author in list(authors_set):
        if len(cur_author) <= 2:
            continue
        if cur_author[0] == "*":
            cur_author = cur_author[1:]
        author_df = papers_df[papers_df["authors_string"].str.contains(cur_author)]
        if cur_author in uncleaned_authors:
            continue

        author_papers_yearly = []
        for year in years_analyzed:
            author_papers_yearly.append(
                author_df[author_df["year"] == str(year)].shape[0]
            )
        total_authors[cur_author] = (sum(author_papers_yearly), author_papers_yearly)

    final_authors = {
        k: v
        for k, v in sorted(
            total_authors.items(), key=lambda item: item[1], reverse=True
        )
    }
    print(max(final_authors.items(), key=operator.itemgetter(1)))

    data_list = list(final_authors.items())
    num_plotted = cfg.citations["n_plotted"]

    if cfg.citations["plot_data"]:
        plt.figure()
    for i in range(num_plotted):
        cur_author = data_list[i][0]
        entry = data_list[i][1][1]

        print("Author: ", cur_author)
        print("Entries: ", final_authors[cur_author])
        print()
        if cfg.citations["plot_data"]:
            plt.plot(years_analyzed, entry, label=str(cur_author))
            plt.legend()

    # CSV Version
    # with open('../Data/AI_Conferences/top_authors.csv', 'r') as affil_csv:
    #     csv_reader = csv.reader(affil_csv)
    #     header = ['author', 'paper_count', 'institution', '2013', '2014', '2015', '2016', '2017', '2018', '2019', 'Notes']
    #     next(csv_reader) # skip header
    #
    #     x_vals = []
    #     y_vals = []
    #     for idx,row in enumerate(csv_reader):
    #         # if idx > 10: break
    #         # print(row)
    #         years = [2013, 2014, 2015, 2016, 2017, 2018, 2019]
    #         author = row[0]
    #         years.append(author)
    #         x_vals.append(years)
    #         new_y = []
    #         for count in row[3:]:
    #             new_y.append(int(count))
    #         new_y.append(0)
    #         y_vals.append(new_y)
    #     y_vals.sort(key=lambda x: -x[5])
    #     # y_vals.sort(key=lambda x: -stdev(x)) # just kinda interesting
    #
    #     plt.figure(figsize=(20,10))
    #     for idx,(x_dat,y_dat) in enumerate(zip(x_vals,y_vals)):
    #         if idx <= 5: plt.plot(x_dat[:-1],y_dat[:-1], label=x_dat[-1])
    #         elif idx > 5 and idx <= 15: plt.plot(x_dat[:-1],y_dat[:-1], alpha = 0.5, label=x_dat[-1])
    #         else: break
    #
    #     plt.legend()
    #     plt.title('Papers per year from top 15 authors through 2019')

# if cfg.citations["top_author_year_exported"]:
#     year = cfg.citations["top_author_year_exported"]
#     df = pd.read_csv('../Data/AI_Conferences/top_authors.csv')
#     df_sorted = df.sort_values(year, ascending=False)
#     df_sorted.to_csv('../Data/AI_Conferences/top_authors_sorted.csv', index=False)

if cfg.citations["export_csv"]:
    print("=====================================")
    print("             EXPORTING CSV           ")
    print("=====================================")
    if not (path.exists(os.getcwd() + "/output")):
        os.mkdir(os.getcwd() + "/output")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    print("/output/filtered_titles_" + timestr + ".csv")
    # papers_df.to_csv(os.getcwd()+'/output/filtered_'+timestr+'.csv')
    if "authors_string" in papers_df.columns:
        titles_df = papers_df[
            [
                "year",
                "title",
                "authors_string",
                "Countries",
                "Institution",
                "Institution Type",
                "OpenSource",
            ]
        ]
        if cfg.citations["keywords"]:
            titles_df.to_csv(
                os.getcwd()
                + "/output/filtered_titles_"
                + timestr
                + "-"
                + cfg.citations["keywords"][0]
                + ".csv"
            )
        else:
            titles_df.to_csv(
                os.getcwd() + "/output/filtered_titles_" + timestr + ".csv"
            )

    else:
        titles_df = papers_df[["year", "title", "authors"]]
        titles_df.to_csv(os.getcwd() + "/output/filtered_titles_" + timestr + ".csv")


plt.show()
