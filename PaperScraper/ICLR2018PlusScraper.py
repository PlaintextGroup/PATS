# This is the scraper for ICLR 2018 and 2019

from bs4 import BeautifulSoup
import requests
import io
import csv
from ResearchPaper import ResearchPaper
from Modules import modules

# ICML 2019
# TODO check how the format changes


class ICLR2018PlusScraper:
    staticmethod

    def scrape_iclr_2018_plus(url, year):
        research_paper_object_list = []

        result = requests.get(url)
        src = result.content
        soup = BeautifulSoup(src, "lxml")
        raw_papers_list = soup.find_all("div", class_="maincard narrower Poster")

        # get all the papers
        for idx, raw_paper in enumerate(raw_papers_list):
            title = raw_paper.find(class_="maincardBody").text
            author_string = raw_paper.find(class_="maincardFooter").contents[0]

            authors = []
            # Get rid of leading new lines and spaces in authors string
            split_list = author_string.split(" · ")
            for string in split_list:
                string = string.strip()
                if string != "":
                    authors.append(string)

            page_url = raw_paper.find("a", href=True, title="PDF")["href"]
            # Pull unique ID
            unique_id = page_url.split("=")[1]
            pdf_url = "https://openreview.net/pdf?id=" + unique_id

            abstract_url = pdf_url.replace("pdf", "forum")
            abs_src = requests.get(abstract_url).content
            soup = BeautifulSoup(abs_src, "lxml")
            abstract = soup.find("span", class_="note-content-value").text.strip()
            abstract = abstract.replace("\n", "")

            # Pull PDF text
            # TODO make sure new method approach is working
            paper_text = modules.pdf_string_from_url(pdf_url)

            this_paper = ResearchPaper(
                unique_id, year, title, pdf_url, authors, paper_text, abstract
            )
            research_paper_object_list.append(this_paper)
            # some feedback that stuff is happening
            print(this_paper.title)
            print("{} / {} ingested".format(idx + 1, len(raw_papers_list)))

        # write to CSV
        with open("iclr" + str(year) + ".csv", "w") as new_csv:
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
