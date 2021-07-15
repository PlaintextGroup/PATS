# This is the scraper for ICLR 2015 and 2016

from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import requests
import io
import csv
from ResearchPaper import ResearchPaper
from Modules import modules


class ICLR20152016Scraper:
    staticmethod

    def scrape_iclr_2015_2016(url, year):
        research_paper_object_list = []

        result = requests.get(url)
        src = result.content
        soup = BeautifulSoup(src, "lxml")
        raw_papers_list = soup.find_all(
            class_="urlextern",
        )
        # get all the papers
        print(url)
        for idx, raw_paper in enumerate(raw_papers_list):
            title = raw_paper.contents[0]
            if (
                str(title) == "[code]"
                or str(title) == "[data]"
                or str(title) == "[video]"
            ):
                continue  # TODO some papers link to [code] or [data] or [video]
            # continue
            # if 'End-to-end' not in title: continue
            author_string = raw_paper
            # print(raw_paper.parent.text)
            # print(raw_paper)
            authors = []
            # Get rid of leading new lines and spaces in authors string
            # print(title)
            # print(raw_paper.next_sibling.next_sibling)
            # author_string = author_string.replace('and', ',')
            author_string = raw_paper.parent.text
            split_list = author_string.split(",")
            # print(author_string)
            for string in split_list:
                string = string.strip()
                if string != "":
                    authors.append(string)

            page_url = raw_paper["href"]
            # Pull unique ID
            unique_id = page_url.split("/")[4]
            # continue
            pdf_url = "https://arxiv.org/pdf/" + unique_id

            abstract_url = pdf_url.replace("pdf", "abs")
            abs_src = requests.get(abstract_url).content
            soup = BeautifulSoup(abs_src, "lxml")
            abstract = soup.find("blockquote", class_="abstract").text.strip()
            if abstract.startswith("Abstract:"):
                abstract = abstract.split("Abstract:")[1].strip()
            abstract = abstract.replace("\n", "")

            # Pull PDF text
            try:
                paper_text = modules.pdf_string_from_url(pdf_url)

                this_paper = ResearchPaper(
                    unique_id, year, title, pdf_url, authors, paper_text
                )
                research_paper_object_list.append(this_paper)
                # some feedback that stuff is happening
                print(this_paper.title)
                print("{} / {} ingested".format(idx + 1, len(raw_papers_list)))
            except KeyboardInterrupt:
                quit()
            except Exception as e:
                print("**** PAPER WITH TITLE [{}] FAILED ****".format(title))
                print(e)

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
