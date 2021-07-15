# NeurIPS webpages that contain paper proceedings from 1987 - 2018 are in the exact same format. This is the scraper.
from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import requests
import io
import csv
from ResearchPaper import ResearchPaper
from Modules import modules


class NeurIPS2019Scraper:
    staticmethod

    def scrape_neurips_2019(url, year):
        # result = requests.get(url)

        # src = result.content
        # soup = BeautifulSoup(src, 'lxml')
        soup = BeautifulSoup(open("./NeurIPS/neurips_2019_src.html"), "html.parser")
        accepted_papers = soup.find("h4").parent
        papers = accepted_papers.find_all("p")
        research_paper_object_list = []
        author_to_affil = {}

        # iterate through all paper urls and create ResearchPaper objects
        print(papers)
        for idx, paper in enumerate(
            papers[2:]
        ):  # skip first two - they are instructional
            title = paper.find("b").text
            authors_and_affils = paper.find("i").text
            authors_and_affils = authors_and_affils.split(" · ")
            authors = []
            affils = []
            for author_and_affil in authors_and_affils:
                author_str, affil_str = author_and_affil.split(" (", 1)
                affil_str = affil_str[:-1]
                authors.append(author_str)
                affils.append(affil_str)
                author_to_affil[
                    author_str
                ] = affil_str  # assuming each author has one affiliation, or it gets overwritten
            assert len(authors) == len(affils)
            # extract the Paper Text
            abstract = "<none>"
            paper_text = "<none>"
            pdf_url = "<none>"
            unique_id = idx
            this_paper = ResearchPaper(
                unique_id, year, title, pdf_url, authors, paper_text, abstract
            )

            research_paper_object_list.append(this_paper)
            print("{} / {} ingested".format(idx + 1, len(papers) - 2))

        # write it all to CSV when everything is ingested
        with open("neurips" + str(year) + ".csv", "w") as new_csv:
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

        with open("author_affiliations.csv", "w") as new_csv:
            writer = csv.writer(new_csv)
            header = ["author_name", "neurips_2019_affil"]
            writer.writerow(header)

            for author, affil in author_to_affil.items():
                row = [author, affil]
                writer.writerow(row)
