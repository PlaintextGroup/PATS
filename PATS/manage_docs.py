import os
import sys
import csv
import ast

import pickle
import unidecode
import collections
from time import sleep

from research_paper import research_paper


def get_paper_to_obj(all_papers):
    paper_to_obj = {}
    for p in all_papers:
        paper_to_obj[(p.conference, p.unique_id)] = p
    return paper_to_obj


def get_paper(all_papers, paper_id):
    for ppr in all_papers:
        if ppr.conference == paper_id[0] and ppr.unique_id == paper_id[1]:
            return ppr
    return None


def get_papers_by_conf(all_papers, conf):
    pprs = []
    for ppr in all_papers:
        if ppr.conference == conf:
            pprs.append(ppr)
    return pprs


def get_all_papers(text_substr_len=None, conf="all"):
    csv.field_size_limit(sys.maxsize)  # cannot read papers otherwise
    sorted_files = sorted(os.listdir("../Data/AI_Conferences/"))
    paper_list = []
    for folder_name in sorted_files:
        if not os.path.isdir("../Data/AI_Conferences/" + folder_name):
            continue
        print(folder_name)
        for fname in os.listdir("../Data/AI_Conferences/{}".format(folder_name)):
            if not fname.endswith("csv"):
                continue
            flag = False
            conference = fname[:-8]
            if conf != "all":
                if conference != conf:
                    continue
            csv_fname = "../Data/AI_Conferences/{}/{}".format(folder_name, fname)
            print(csv_fname)
            with open(csv_fname, newline="") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                next(csv_reader)  # skip header
                for idx, row in enumerate(csv_reader):
                    try:
                        if len(row) > 6:
                            ppr_abs = row[6]
                        else:
                            ppr_abs = "<none>"
                            flag = True
                        new_paper = research_paper(
                            row[0],
                            row[1],
                            row[2],
                            row[4],
                            row[3],
                            row[5],
                            ppr_abs,
                            conference,
                        )
                        try:
                            new_paper.authors = ast.literal_eval(new_paper.authors)
                        except:
                            pass  # TODO fix this for some papers
                        if text_substr_len:
                            new_paper.paper_text = new_paper.paper_text[
                                :text_substr_len
                            ]
                        paper_list.append(new_paper)
                    except Exception as e:
                        print("Failed on [{}]".format(fname))
                        print("{}{}".format("\t", row[2]))
                        print("*" * 10)
                        print("\t {}".format(e))
                        quit()
            if flag:
                print("Problem reading abstracts for {}".format(fname))

    return paper_list


def get_papers_without_references(papers):
    ### TODO
    ### Right now, this just tries to cut out paper references, which we would need to at least try before analyzing categories
    num_split = 0
    split_papers = []
    for idx, paper in enumerate(papers):
        if "References" in paper.paper_text:
            paper.paper_text = paper.paper_text.rsplit("References", 1)[0]
            split_papers.append(paper)
            num_split += 1
        elif "Refrences" in paper.paper_text:
            paper.paper_text = paper.paper_text.rsplit("Refrences", 1)[0]
            split_papers.append(paper)
            num_split += 1
        elif "Bibliography" in paper.paper_text:
            paper.paper_text = paper.paper_text.rsplit("Refrences", 1)[0]
            split_papers.append(paper)
            num_split += 1
        else:
            split_papers.append(paper)
        if idx % 100 == 0:
            print("{} / {}".format(idx, len(papers)))
    print("Split for {} / {}".format(num_split, len(papers)))
    return split_papers


def get_chinese_name_list():
    name_and_alts = []
    with open(
        "./lookup_tables/Chinese Surnames [ASCII] - Sheet1.csv", "r"
    ) as name_file:
        csv_reader = csv.reader(name_file, delimiter=",")
        next(csv_reader)
        for line in csv_reader:
            aliases = []
            for item in line:
                if item == "":
                    break  # no more items
                aliases.append(item)
            name_and_alts.append(aliases)
        return name_and_alts
    return []


"""
Return list of tuples, where each tuple is list of aliases, country, and institution type.
"""


def get_institution_list():
    inst_to_alts = []
    with open(
        "./lookup_tables/AI Research Institutions - Institution List.csv", "r"
    ) as inst_file:
        csv_reader = csv.reader(inst_file, delimiter=",")
        next(csv_reader)
        for line in csv_reader:
            country = line[0]
            inst_type = line[1]
            aliases = []
            for item in line[2:]:
                if item == "":
                    break  # no more items
                aliases.append(item)
            # print(aliases, country, inst_type)
            inst_to_alts.append((aliases, country, inst_type))
            # print(inst_to_alts)
            # quit()
        return inst_to_alts
    return []


def get_category_dict():
    cat_to_keywords = collections.defaultdict(set)
    with open(
        "./lookup_tables/God AI keywords - Initial Focus Areas.csv", "r"
    ) as kw_file:
        csv_reader = csv.reader(kw_file, delimiter=",")
        next(csv_reader)
        for line in csv_reader:
            cat_name = line[0]
            aliases = []
            # if kw_type != 'category': continue
            for item in line[1:]:
                if item == "":
                    break  # no more items
                cat_to_keywords[cat_name].add(item)
        return cat_to_keywords
    return {}


def get_author_affil():
    name_to_affil = {}
    with open("../Data/AI_Conferences/author_affiliations.csv", "r") as affil_csv:
        csv_reader = csv.reader(affil_csv, delimiter=",")
        next(csv_reader)
        for line in csv_reader:
            name = line[0]
            inst = line[1]
            name_to_affil[name] = inst
        all_institutions = get_institution_list()
        for name, affil in name_to_affil.items():
            for aliases, _, _ in all_institutions:
                for alias in aliases[1:]:
                    if alias.strip() == affil.strip():  # TODO
                        # if editdistance.eval(alias.strip(), affil.strip()) < 3:
                        # print('substituting {} for {} for {}'.format(affil,aliases[0],name))
                        name_to_affil[name] = aliases[0]
                        break
    return name_to_affil


def get_titles():
    return set()


def get_paper_to_inst(conf="neurips"):
    # TODO do better with other conferences
    # if conf == 'neurips':
    #     with open('../R_Analysis/neurIPS_2013_to_2019_insts.csv', 'r') as inst_csv:
    #         id_to_inst = collections.defaultdict(list)
    #         csv_reader = csv.reader(inst_csv, delimiter=',')
    #         next(csv_reader) # skip header
    #         for idx,row in enumerate(csv_reader):
    #             paper_id = row[0]
    #             inst = row[1]
    #             id_to_inst[(conf,paper_id)].append(inst)
    #             # if inst_list == '[]':
    #             #     inst_list = []
    #             # else:
    #             #     inst_list = ast.literal_eval(inst_list)
    # return id_to_inst
    ppr_to_inst = {}
    with open("./lookup_tables/papers_to_insts.csv", "r") as inst_csv:
        csv_reader = csv.reader(inst_csv, delimiter=",")
        next(csv_reader)  # skip header
        for idx, row in enumerate(csv_reader):
            conf = row[0]
            unique_id = row[1]
            insts = ast.literal_eval(row[2])
            ppr_to_inst[(conf, unique_id)] = insts
    return ppr_to_inst


def get_id_to_code_url():
    id_to_code = {}
    with open("./lookup_tables/papers_to_code.csv", "r") as code_csv:
        csv_reader = csv.reader(code_csv, delimiter=",")
        next(csv_reader)  # skip header
        for idx, row in enumerate(csv_reader):
            conf = row[0]
            paper_id = row[1]
            # title = row[2]
            code_urls = row[3]
            id_to_code[(conf, paper_id)] = code_urls
    return id_to_code


def get_title_to_conference():
    title_to_conference = {}
    with open("./lookup_tables/paper_to_conf.csv", "r") as title_csv:
        csv_reader = csv.reader(title_csv, delimiter=",")
        next(csv_reader)  # skip header
        for idx, row in enumerate(csv_reader):
            title = row[0]
            conf = row[1]
            title_to_conference[title] = conf
    return title_to_conference


def get_title_to_data():
    return {}


def get_conference_data(conf_name, year):
    csv_path = "../Data/{}/{}{}.csv".format(conf_name.upper(), conf_name.lower(), year)
    return {}


def get_inst_to_inst_type():
    inst_list = get_institution_list()
    inst_to_type = {}
    for aliases, country, inst_type in inst_list:
        if len(aliases) == 0:
            continue
        inst_to_type[aliases[0].strip()] = inst_type  # TODO STRIP here
    return inst_to_type


def get_inst_to_country():
    inst_list = get_institution_list()
    inst_to_country = {}
    for aliases, country, inst_type in inst_list:
        for alias in aliases:  # TODO works for all aliases, or just first?
            inst_to_country[alias] = country
        # inst_to_country[aliases[0]] = country
    return inst_to_country


def write_id_to_conference():
    id_to_conference = {}
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
                csv_reader = csv.reader(csv_file, delimiter=",")
                next(csv_reader)  # skip header
                # try:
                for idx, row in enumerate(csv_reader):
                    paper_id = row[0]
                    title = row[2]
                    id_to_conference[(conf, paper_id)] = fname[:-8]
                # except Exception as e:
                #     print('Failed on [{}]'.format(fname))
                #     print('{}{}'.format('\t', row))
                #     print('-'*10)
                #     print('\t {}'.format(e))

    with open("./lookup_tables/paper_to_conf.csv", "w") as new_csv:
        writer = csv.writer(new_csv)
        header = ["title", "conference"]
        writer.writerow(header)
        for c, id, conf in id_to_conference.items():
            row = [c, id, conf]
            writer.writerow(row)
    print("Done writing title to conference")


def write_paper_to_insts():
    csv.field_size_limit(sys.maxsize)  # cannot read papers otherwise
    inst_to_alts = get_institution_list()
    paper_list = get_all_papers()
    name_to_affil = get_author_affil()  # TODO this only works for NeurIPS 2019...
    print("Matching")
    num_p = 0
    max_p = 5000
    lines = []
    num_untagged = 0  # num untagged
    num_tagged = 0
    for idx, paper in enumerate(paper_list):
        # print(idx)
        paper_text = paper.paper_text
        inst_in_paper = []
        if paper.conference == "neurips" and paper.year == 2019:
            print(paper.title)
        pp_text = paper_text[:1000]
        pp_text = unidecode.unidecode(pp_text)
        for (aliases, country, inst_type) in inst_to_alts:
            for alias in aliases:
                # pp_text = pp_text.replace('’', '\'')
                if (
                    alias in pp_text or alias in paper_text[:1000]
                ):  # TODO matching is first XX characters?
                    inst_in_paper.append(aliases[0])
                    break
        if len(inst_in_paper) == 0 and num_p < max_p:
            l_1 = "{} {} {} {} {}".format(
                paper.conference,
                paper.year,
                paper.unique_id,
                paper.title,
                paper.pdf_url,
            )
            l_2 = paper_text[:1000]
            # lines += [l_1, l_2]
            lines += [l_2[:500]]
            # print(l_1)
            # print()
            num_p += 1
            num_untagged += 1
        if num_p >= max_p:
            quit()
        if (
            len(inst_in_paper) == 0
            and paper.conference == "neurips"
            and paper.year == "2019"
        ):  # not ideal but we have these affiliations...
            for author in paper.authors:
                if author not in name_to_affil:
                    continue
                author_affil = name_to_affil[author]
                inst_in_paper.append(author_affil)
            print(paper.conference, paper.unique_id, paper.pdf_url)
            print(inst_in_paper)
        if len(inst_in_paper) > 0:
            num_tagged += 1
        paper_list[idx] = [paper.conference, paper.unique_id, inst_in_paper]
    with open("garbagedump.txt", "w") as gd:
        for line in lines:
            gd.write(line + "\n")

    with open("./lookup_tables/papers_to_insts.csv", "w") as new_csv:
        writer = csv.writer(new_csv)
        header = ["conference", "unique_id", "institutions"]
        writer.writerow(header)
        for idx, paper in enumerate(paper_list):
            row = paper
            writer.writerow(row)
    print("Done writing paper to institutions")
    print("Did not tag {} papers".format(num_untagged))
    print("Did tag {} papers".format(num_tagged))


# write_paper_to_insts()
# write_id_to_conference() # don't need this anymore

try:
    f = open("papers2.p")
except IOError:
    print("No papers2.p")
    papers_tmp = get_all_papers(text_substr_len=None)
    outfile = open("papers2.p", "wb")
    pickle.dump(papers_tmp, outfile)
    outfile.close()
    write_paper_to_insts()
    print("Done creating papers2.p")
