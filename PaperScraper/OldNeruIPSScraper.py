# NeurIPS webpages that contain paper proceedings from 1987 - 2018 are in the exact same format. This is the scraper.
from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import requests
import io
import csv
from ResearchPaper import ResearchPaper
from Modules import modules


class OldNeurIPSScraper:
    staticmethod

    def scrape_old_neurips(url, year):
        result = requests.get(url)

        num_paper = 1
        src = result.content
        soup = BeautifulSoup(src, "lxml")
        links = soup.find_all("a")
        paper_url_list = []
        research_paper_object_list = []

        # get all the paper urls
        for link in links:
            if "/paper/" in link.attrs["href"]:
                paper_url_list.append(link.attrs["href"])

        # iterate through all paper urls and create ResearchPaper objects
        for idx, paper_url in enumerate(paper_url_list):
            paper_scr = requests.get("https://papers.nips.cc" + paper_url).content
            paper_soup = BeautifulSoup(paper_scr, "lxml")

            # parse unique ID from paper URL
            url_chunks = paper_url.split("/")
            url_chunks2 = url_chunks[2].split("-")
            unique_id = url_chunks2[0]

            # Parse out title
            title = paper_soup.find("title").contents[0]

            # parse out the substring "/paper/" from url to get pdf_name
            pdf_name = paper_url.split("/")[2] + ".pdf"

            # extract authors
            authors = []
            authors_html = paper_soup.find_all("li", class_="author")
            for html in authors_html:
                authors.append(html.contents[0].contents[0])

            # extract abstract
            abstract_url = "http://papers.nips.cc" + paper_url
            abs_src = requests.get(abstract_url).content
            soup = BeautifulSoup(abs_src, "lxml")
            abstract = soup.find("p", class_="abstract").text.strip()
            abstract = abstract.replace("\n", "")
            # print(abstract_url)
            # print(abstract)

            # extract the Paper Text
            pdf_url = "https://papers.nips.cc" + "/paper/" + pdf_name
            paper_text = modules.pdf_string_from_url(pdf_url)
            this_paper = ResearchPaper(
                unique_id, year, title, pdf_url, authors, paper_text, abstract
            )

            research_paper_object_list.append(this_paper)
            print("{} / {} ingested".format(idx + 1, len(paper_url_list)))
            num_paper += 1

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
