#!/usr/bin/env python
# coding: utf-8

# ### Scraping

# In[2]:


from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import requests
import io
import sys
import csv
from ResearchPaper import ResearchPaper
from Modules import modules
import re


parent_url = "http://openaccess.thecvf.com/"

conf_url_list = [
    "http://openaccess.thecvf.com/ICCV2019.py",
    "http://openaccess.thecvf.com/CVPR2019.py",
    "http://openaccess.thecvf.com/CVPR2018.py",
    "http://openaccess.thecvf.com/ICCV2017.py",
    "http://openaccess.thecvf.com/CVPR2017.py",
    "http://openaccess.thecvf.com/CVPR2016.py",
    "http://openaccess.thecvf.com/ICCV2015.py",
    "http://openaccess.thecvf.com/CVPR2015.py",
    "http://openaccess.thecvf.com/CVPR2014.py",
    "http://openaccess.thecvf.com/ICCV2013.py",
    "http://openaccess.thecvf.com/CVPR2013.py",
    "http://openaccess.thecvf.com/ECCV2018.py",
]
# current_conf_url = 'http://openaccess.thecvf.com/CVPR2019.py'

# Get High Level Scrapping Stats
total_papers_avail = []
num_papers_collected = []
num_err_papers = []
pct_errs = []


# CVPR 2019
# current_conf_url = 'http://openaccess.thecvf.com/CVPR2019.py'
current_conf_url = conf_url_list[11]
current_conf = current_conf_url[-11:-3]  # get current conf
research_paper_object_list = []
result = requests.get(current_conf_url)
src = result.content
soup = BeautifulSoup(src, "lxml")
papers_with_errors = set()


# Get titles
title_list = soup.find_all("dt", class_="ptitle")
titles = [title.get_text() for title in title_list]
total_papers_avail.append(len(titles))


# Set Unique IDs
# If CVPR, then * 2877
# If ICCV, then * 4228
# If ECCV, then * 3228
if current_conf[0:4] == "CVPR":
    unique_ids = [2019 * 2877 * i for i in range(1, len(title_list) + 1)]
elif current_conf[0:4] == "ICCV":
    unique_ids = [2019 * 4228 * i for i in range(1, len(title_list) + 1)]
else:
    unique_ids = [2019 * 3228 * i for i in range(1, len(title_list) + 1)]


# In[9]:


# Remove all line breaks
for e in soup.findAll("br"):
    e.extract()


# In[10]:


raw_papers = soup.find_all(class_="bibref")
authors = []
year = []
for raw_paper in raw_papers:
    single_paper = raw_paper.text.split("\n")
    for text in single_paper:
        if text != "" and len(text.split("=")) > 1:
            header = text.split("=")[0]
            body = text.split("=")[1]
            if header == "author ":
                # Clean out braces and split according to 'and'
                cleaned_body = body.replace(" {", "").replace("}", "").split(" and ")
                paper_authors = []
                for name in cleaned_body:
                    last_name = name.split(",")[0]
                    first_name = name.split(",")[1]
                    #                     print(first_name + ' ' + last_name)
                    paper_authors.append(first_name + " " + last_name)
                authors.append(paper_authors)
            # Get title if the above method doesn't work
            #         if header = 'title':
            #             # Clean out braces, commas and spaces
            #             cleaned_body = body.replace('{','').replace('}','').replace(',','')[1:]
            #             titles.append(cleaned_body)
            if header == "year ":
                year.append(body.replace(" {", "").replace("}", ""))


# In[11]:


# Get paper texts and PDF Urls

pdf_list = soup.find_all(href=re.compile("/papers/"))
paper_text = []
pdf_urls = []
# Check length of PDF List matches length of UNIQUE IDS
if len(pdf_list) == len(unique_ids):
    for count, pdf in enumerate(pdf_list):
        try:
            pdf_url = parent_url + pdf_list[count].get("href")
            paper_text.append(modules.pdf_string_from_url(pdf_url))
            pdf_urls.append(pdf_url)
            print(
                "**** PAPER NUMBER [{}] WITH URL [{}] ADDED ****".format(
                    unique_ids[count], pdf_url
                )
            )
        except:
            paper_text.append("FAILED")
            pdf_urls.append("FAILED")
            papers_with_errors.add(unique_ids[count])
            print(
                "**** PAPER NUMBER [{}] WITH URL [{}] FAILED ****".format(
                    unique_ids[count], pdf_url
                )
            )
else:
    print(
        "**** LENGTH OF PDF LIST [{}] DOES NOT MATCH LENGTH OF UNIQUE IDS [{}] ****".format(
            len(pdf_list), len(unique_ids)
        )
    )


# In[12]:


# Grab all abstracts

abstracts = []
abs_list = soup.find_all(class_="ptitle")

# Check that length of the abstract list matches that of the UNIQUE IDS
if len(abs_list) == len(unique_ids):
    for count, abstract in enumerate(abs_list):
        try:
            abstract_url = parent_url + abs_list[count].contents[0].get("href")
            abs_src = requests.get(abstract_url).content
            abs_soup = BeautifulSoup(abs_src, "lxml")
            abstracts.append(abs_soup.find_all(id="abstract")[0].text)
        except:
            abstracts.append("FAILED")
            papers_with_errors.add(unique_ids[count])
            print(
                "**** PAPER NUMBER [{}] WITH URL [{}] FAILED ****".format(
                    unique_ids[count], abstract_url
                )
            )
else:
    print(
        "**** LENGTH OF ABS LIST [{}] DOES NOT MATCH LENGTH OF UNIQUE IDS [{}] ****".format(
            len(abs_list), len(unique_ids)
        )
    )


# In[13]:


for idx, unique_id in enumerate(unique_ids):
    if unique_id not in papers_with_errors:
        this_paper = ResearchPaper(
            unique_ids[idx],
            year[idx],
            titles[idx],
            pdf_urls[idx],
            authors[idx],
            paper_text[idx],
            abstracts[idx],
        )
        research_paper_object_list.append(this_paper)


# In[19]:


print("*** NUMBER OF PAPERS COLLECTED: {} ***".format(len(research_paper_object_list)))
print("*** NUMBER OF PAPERS WITH ERRORS: {} ***".format(len(papers_with_errors)))
print(
    "*** % OF PAPERS WITH ERRORS: {} ***".format(
        len(papers_with_errors) / len(research_paper_object_list) * 100
    )
)


# In[15]:


# Write to CSV
with open(current_conf + ".csv", "w") as new_csv:
    writer = csv.writer(new_csv)
    header = [
        "unique_id",
        "year",
        "title",
        "authors",
        "pdf_url",
        "paper_text",
        "abstract",
    ]
    writer.writerow(header)

    for paper in research_paper_object_list:
        row = [
            paper.unique_id,
            paper.year,
            paper.title,
            paper.authors,
            paper.pdf_url,
            paper.paper_text,
            paper.abstract,
        ]
        writer.writerow(row)
