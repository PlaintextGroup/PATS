# NeurIPS webpages that contain paper proceedings from 1987 - 2018 are in the exact same format. This is the scraper.
from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import requests
import io
import sys
import csv
from ResearchPaper import ResearchPaper
from Modules import modules

# ICML 2019
# TODO check how the format changes


class ICMLScraper:
    staticmethod

    def scrape_icml(url, year):
        research_paper_object_list = []

        result = requests.get(url)
        src = result.content
        soup = BeautifulSoup(src, "lxml")
        raw_papers_list = soup.find_all("div", class_="paper")

        # get all the papers
        for idx, raw_paper in enumerate(raw_papers_list):
            title = raw_paper.find(class_="title").text
            author_string = raw_paper.find(class_="authors").contents[0]

            authors = []
            # Get rid of leading new lines and spaces in authors string
            split_list = author_string.split("\n")
            for string in split_list:
                string = string.strip()
                if string != "":
                    authors.append(string)

            # Manage edge case of different PDF href text in 2015
            if year == 2015:
                pdf_url = raw_paper.find("a", href=True, text="pdf")["href"]
            else:
                pdf_url = raw_paper.find("a", href=True, text="Download PDF")["href"]

            abstract_url = raw_paper.find("a", href=True, text="abs")["href"]
            abs_src = requests.get(abstract_url).content
            soup = BeautifulSoup(abs_src, "lxml")
            abstract = soup.find("div", class_="abstract").text.strip()
            abstract = abstract.replace("\n", "")

            # Pull unique ID
            unique_id = pdf_url.split("/")[4]

            # Pull PDF text
            # TODO make sure new method approach is working
            try:
                paper_text = modules.pdf_string_from_url(pdf_url)

                this_paper = ResearchPaper(
                    unique_id, year, title, pdf_url, authors, paper_text, abstract
                )
                research_paper_object_list.append(this_paper)
                # some feedback that stuff is happening
                print(
                    "{} / {} {}".format(idx + 1, len(raw_papers_list), this_paper.title)
                )
            except KeyboardInterrupt:
                quit()
            except:
                print("**** PAPER WITH TITLE [{}] FAILED ****".format(title))

        with open("icml" + str(year) + ".csv", "w") as new_csv:
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
