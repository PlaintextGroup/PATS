# https://openreview.net/group?id=ICLR.cc/2017/conference
# Need to put RENDERED SOURCE into ICLR/*.html

from bs4 import BeautifulSoup
import io
import csv
import requests

from Modules import modules
from ResearchPaper import ResearchPaper


class ICLR2017Scraper:
    staticmethod

    def scrape_iclr_2017(
        url, year
    ):  # TODO year only added for conformity with other scrapers
        assert year == 2017
        research_paper_object_list = []

        soup = BeautifulSoup(open("./ICLR/ICLR_2017.html"), "html.parser")
        raw_papers_list = soup.find_all("div", class_="note panel")
        for idx, raw_paper in enumerate(raw_papers_list):
            title = raw_paper.find(class_="note_content_title").text

            meta_rows = raw_paper.find_all(class_="meta_row")
            authors = meta_rows[0].find_all("a")
            decision = meta_rows[3]
            if "ICLR 2017 Conference Reject" in decision.text:
                continue

            base_url = "https://openreview.net"
            pdf_row = raw_paper.find(class_="title_pdf_row clearfix")
            pdf_url = pdf_row.find("a", href=True, title="Download PDF")["href"]
            if "http" not in pdf_url:
                pdf_url = (
                    base_url + pdf_url
                )  # TODO this is a problem for a few that have full urls...

            try:
                unique_id = pdf_url.split("id=")[1]
            except:
                unique_id = pdf_url.split("/")[-1].split(".pdf")[0]

            abstract_url = (
                base_url + raw_paper.find(class_="note_content_title").find("a")["href"]
            )
            abs_src = requests.get(abstract_url).content
            soup = BeautifulSoup(abs_src, "lxml")
            abstract = soup.find("span", class_="note-content-value").text.strip()
            abstract = abstract.replace("\n", "")

            authors = [a.text for a in authors]

            paper_text = modules.pdf_string_from_url(pdf_url)
            this_paper = ResearchPaper(
                unique_id, year, title, pdf_url, authors, paper_text
            )
            research_paper_object_list.append(this_paper)
            print("{} / {} {}".format(idx + 1, len(raw_papers_list), this_paper.title))

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
