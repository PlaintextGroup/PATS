import math
import random
import operator
import collections

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import editdistance

from ManageDocs import *

# write_title_to_conference()

# all_neurips = get_all_papers(conf='neurips')
# all_neurips = get_all_papers()

infile = open("papers.p", "rb")
import pickle

all_neurips = pickle.load(infile)
infile.close()

paper_to_inst = get_paper_to_inst()
name_to_affil = get_author_affil()

print("Data assembled")
num_neurips = 0
num_untagged = 0
top_publishing_neurips = collections.defaultdict(int)
for idx, paper in enumerate(all_neurips):
    num_neurips += 1
    insts = paper_to_inst[(paper.conference, paper.unique_id)]

    # print(paper.authors, paper.conference)
    # if idx > 1000: quit()
    if isinstance(paper.authors, str):
        paper.authors = paper.authors.split(", ")  # TODO

    if len(insts) == 0:
        for author in paper.authors:
            if author in name_to_affil:
                insts.append(name_to_affil[author])
    if len(insts) == 0:
        num_untagged += 1
    for inst in insts:
        top_publishing_neurips[inst] += 1

print("{}/{} untagged".format(num_untagged, num_neurips))
top_ten = sorted(top_publishing_neurips.items(), key=lambda item: -item[1])[:10]
print(top_ten)

author_to_count = collections.defaultdict(int)
author_to_yearly_count = collections.defaultdict(lambda: collections.defaultdict(int))
for paper in all_neurips:
    for author in paper.authors:
        author_to_count[author] += 1
        author_to_yearly_count[author][paper.year] += 1
top_authors = sorted(author_to_count.items(), key=lambda item: -item[1])

years = ["2013", "2014", "2015", "2016", "2017", "2018", "2019"]
with open("../Data/AI_Conferences/top_authors.csv", "w") as affil_csv:
    writer = csv.writer(affil_csv)
    header = [
        "author",
        "paper_count",
        "institution",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018",
        "2019",
        "Notes",
    ]
    writer.writerow(header)
    for idx, (auth, count) in enumerate(top_authors):
        inst = name_to_affil[auth] if auth in name_to_affil else "<none>"
        row = [auth, count, inst]
        for year in years:
            row.append(author_to_yearly_count[auth][year])
        writer.writerow(row)

if False:
    # bar chart of top n institutions
    top_n_auth = top_ten
    plt.figure(figsize=(12, 8))
    keys = [x[0] for x in top_n_auth]
    vals = [x[1] for x in top_n_auth]
    freq_series = pd.Series.from_array(vals)
    ax = freq_series.plot(kind="bar")
    plt.bar(range(len(vals)), vals, align="center")
    plt.xticks(range(len(keys)), ["" for x in keys], rotation=45)
    # https://stackoverflow.com/questions/28931224/adding-value-labels-on-a-matplotlib-bar-chart
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
elif False:
    # Bar chart of top n authors
    top_n_auth = top_authors[:20]
    plt.figure(figsize=(12, 8))
    keys = [x[0] for x in top_n_auth]
    vals = [x[1] for x in top_n_auth]
    freq_series = pd.Series.from_array(vals)
    ax = freq_series.plot(kind="bar")
    plt.bar(range(len(vals)), vals, align="center")
    plt.xticks(range(len(keys)), ["" for x in keys], rotation=45)
    # https://stackoverflow.com/questions/28931224/adding-value-labels-on-a-matplotlib-bar-chart
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

elif False:
    # Pie chart of institution types
    inst_to_type = get_inst_to_inst_type()
    type_to_count = collections.defaultdict(float)
    for paper in all_neurips:
        insts = paper_to_inst[(paper.conference, paper.unique_id)]
        for inst in insts:
            if inst.strip() not in inst_to_type:
                continue
            inst_type = inst_to_type[inst.strip()]
            type_to_count[inst_type] += 1
    print(type_to_count)
    plt.pie(
        list(type_to_count.values()), labels=list(type_to_count.keys()), autopct=None
    )
    plt.show()

elif False:
    # Pie chart of institution countries
    inst_to_country = get_inst_to_country()
    country_to_count = collections.defaultdict(float)
    for paper in all_neurips:
        insts = paper_to_inst[(paper.conference, paper.unique_id)]
        for inst in insts:
            if inst.strip() in inst_to_country:
                inst_country = inst_to_country[inst.strip()]
                country_to_count[inst_country] += 1
    threshold = 50
    other_num = sum([v for k, v in country_to_count.items() if v < threshold])
    new_country_count = {k: v for k, v in country_to_count.items() if v >= threshold}
    new_country_count["Other"] = other_num
    print(new_country_count)
    plt.pie(
        list(new_country_count.values()),
        labels=list(new_country_count.keys()),
        autopct=None,
    )
    plt.show()

elif True:
    # Count number of Chinese names
    print("Chinese surnames")
    chinese_names = get_chinese_name_list()
    count_chinese = 0
    for author, _ in top_authors:
        last_name = author.split(" ")[-1]
        found_chinese = False
        for aliases in chinese_names:
            if not found_chinese:
                for alias in aliases:
                    if last_name == alias:
                        count_chinese += 1
                        found_chinese = True
                        # s = '{}, {}, {} : {}\n'.format(alias, author, last_name, aliases)
                        # print(s.replace('\n',''))
                        break
            else:
                break

    top_n_authors = top_authors[:30]
    # print(top_n_authors)
    print("Found {} / {} Chinese names".format(count_chinese, len(top_authors)))

    auth_keys = [x[0] for x in top_n_authors]
    auth_vals = [x[1] for x in top_n_authors]
    plt.barh(range(len(auth_vals)), auth_vals, align="center")
    plt.yticks(range(len(auth_keys)), auth_keys, rotation=0)
    plt.subplots_adjust(left=0.4)
    plt.show()

elif True:
    # Create graph for authors or institutions
    inst_to_country = get_inst_to_country()
    G = nx.Graph()
    G_2 = nx.Graph()  # institutions
    G_3 = nx.Graph()

    if False:
        for paper in all_neurips:
            insts = paper_to_inst[(paper.conference, paper.unique_id)]
            if len(insts) < 2:
                continue
            insts = [
                inst for inst in insts if inst in inst_to_country
            ]  # remove the ones we don't know UNCOMMENT TO ADD MORE INSTITUTIONS
            for inst_1 in insts:
                for inst_2 in insts:
                    if inst_1 == inst_2:
                        continue
                    try:
                        c_1 = inst_to_country[inst_1]
                        c_2 = inst_to_country[inst_2]
                    except:
                        print("Failed for [{}] or [{}]".format(inst_1, inst_2))
                    if G_3.has_edge(c_1, c_2):
                        G_3.add_edge(c_1, c_2, weight=G_3[c_1][c_2]["weight"] + 0.5)
                    else:
                        G_3.add_edge(c_1, c_2, weight=0.5)

        to_remove = set()
        for u, v, d in G_3.edges(data=True):
            weight = d["weight"]
            if weight < 50:
                # G_3.remove_edge(u,v)
                to_remove.add((u, v))
        G_3.remove_edges_from(to_remove)
        G_3.remove_nodes_from(list(nx.isolates(G_3)))

        d = dict(G_3.degree)
        edge_labels = nx.get_edge_attributes(G_3, "weight")
        pos = nx.spring_layout(G_3)
        nx.draw(
            G_3,
            pos=pos,
            nodelist=d.keys(),
            node_size=[v * 40 + 40 for v in d.values()],
            with_labels=True,
            font_size=10,
        )
        nx.draw_networkx_edge_labels(
            G_3,
            pos,
            edge_labels=edge_labels,
            font_size=8,
            font_family="Proxima Nova Alt",
        )
        plt.show()
        deg_cen = nx.degree_centrality(G_3)
        print(deg_cen)

    elif True:
        for paper in all_neurips:
            authors = paper.authors
            for author_1 in authors:
                for author_2 in authors:
                    if author_1 != author_2:
                        if G.has_edge(author_1, author_2):
                            G.add_edge(
                                author_1,
                                author_2,
                                weight=G[author_1][author_2]["weight"] + 0.5,
                            )
                        else:
                            G.add_edge(author_1, author_2, weight=0.5)

                        # we have affiliations for both authors
                        if author_1 in name_to_affil and author_2 in name_to_affil:
                            inst_1 = name_to_affil[author_1]
                            inst_2 = name_to_affil[author_2]

                            if inst_1 == inst_2:
                                continue
                            if G_2.has_edge(inst_1, inst_2):
                                G_2.add_edge(
                                    inst_1,
                                    inst_2,
                                    weight=G_2[inst_1][inst_2]["weight"] + 0.5,
                                )
                            else:
                                G_2.add_edge(inst_1, inst_2, weight=0.5)

                            # add to graphs
        if False:
            for idx, (auth, count) in enumerate(top_authors):
                if idx < 50:
                    continue
                try:
                    G.remove_node(auth)
                except:
                    pass
            # top_collaborators = sorted(G.degree, key=lambda item: -item[1])
            # for idx,(auth,count) in enumerate(top_collaborators):
            #     if idx < 10: continue
            #     try:
            #         G.remove_node(auth)
            #     except:
            #         pass
            G.remove_nodes_from(list(nx.isolates(G)))

            mapping = {}
            # for author in author_to_coauthors:
            #     new_name = author.replace(' ', '\n')
            #     mapping[author] = new_name
            d = dict(G.degree)
            edge_labels = nx.get_edge_attributes(G, "weight")
            edge_labels = nx.get_edge_attributes(G, "weight")
            edge_labels = nx.get_edge_attributes(G, "weight")
            edge_labels = nx.get_edge_attributes(G, "weight")
            edge_labels = nx.get_edge_attributes(G, "weight")
            pos = nx.spring_layout(G)
            nx.draw(
                G,
                pos=pos,
                nodelist=d.keys(),
                node_size=[v * 40 + 40 for v in d.values()],
                with_labels=True,
                font_size=8,
            )
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
            nx.relabel_nodes(G, mapping)
            plt.show()

        elif True:
            papers_per_institution = collections.defaultdict(int)
            for paper in all_neurips:
                authors = paper.authors
                for author in authors:
                    if author not in name_to_affil:
                        continue
                    affil = name_to_affil[author]
                    papers_per_institution[affil] += 1
            top_institutions = sorted(
                papers_per_institution.items(), key=lambda item: -item[1]
            )
            # print(sorted(G_2.degree, key=lambda x: -x[1]))
            print(top_institutions[:10])
            for idx, (auth, count) in enumerate(top_institutions):
                if idx < 10:
                    continue
                try:
                    G_2.remove_node(auth)
                except:
                    pass
            # print(institution_to_institution)
            # print(G_2.nodes.data())
            # for idx,(auth,count) in enumerate(top_authors):
            #     if idx < 100: continue
            #     G.remove_node(auth)
            # to_remove = set()
            # for node,deg in G_2.degree:
            #     print(node,deg)
            #     if deg < 35:
            #         to_remove.add(node)
            # for node in to_remove: G_2.remove_node(node)
            # G_2.remove_nodes_from(list(to_remove))
            d = dict(G_2.degree)
            # edge_labels = nx.get_edge_attributes(G,'weight')
            # edge_labels=nx.draw_networkx_edge_labels(G,pos=nx.spring_layout(G)))
            print(G_2.edges())
            max_weight = max([G_2[e[0]][e[1]]["weight"] for e in G_2.edges()])
            edge_alphas = [G_2[e[0]][e[1]]["weight"] / max_weight for e in G_2.edges()]

            edge_labels = nx.get_edge_attributes(G_2, "weight")
            pos = nx.spring_layout(G_2)
            # colors = [random_color() for u,v in G_2.edges()]
            weights = [math.sqrt(G_2[u][v]["weight"]) for u, v in G_2.edges()]
            nx.draw(
                G_2,
                pos=pos,
                nodelist=d.keys(),
                node_size=[v * v + 10 for v in d.values()],
                with_labels=True,
                font_size=12,
                width=weights,
            )
            print(edge_alphas)
            # edges = nx.draw_networkx_edges(G_2, pos, edge_colors=edge_alphas)
            # for idx in range(G_2.number_of_edges()):
            # for idx,e in enumerate(G_2.edges(data=True)):
            #     e.set_alpha(edge_alphas[idx])
            # nx.draw_networkx_edge_labels(G_2, pos, edge_labels=edge_labels, font_size=6)
            plt.show(block=True)
