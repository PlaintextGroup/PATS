from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import urllib
import requests
import io
import csv
import urllib.parse
from Modules import modules
from ResearchPaper import ResearchPaper


class AAAIScraper:
    staticmethod

    def scrape_aaai(url, year):
        research_paper_object_list = []

        result = requests.get(url)
        src = result.content
        print(url)
        soup = BeautifulSoup(src, "lxml")
        raw_papers_list = soup.find_all("p", class_="left")

        for idx, raw_paper in enumerate(raw_papers_list):
            authors = raw_paper.find("i").contents[0]

            # Title
            title = raw_paper.find("a", href=True).text.lstrip()
            if title in [
                "AAAI Organization",
                "Conference Committees",
                "Awards",
                "Sponsors",
                "IAAI-13 Preface",
                "AAAI-13 Preface",
                "EAAI-13 Preface",
                "Invited Talks",
            ]:
                print("skip {}".format(title))
                continue

            # PDF URL
            if year == 2019:
                pdf_url = raw_paper.find("a", href=True, text="PDF")["href"]
            else:
                # TODO commented out somehow...
                pdf_url = (
                    str(raw_paper)
                    .split("<!-- ")[1]
                    .split(" -->")[0]
                    .split('href="')[1]
                    .split('" class')[0]
                )
                pdf_url = pdf_url.replace("view", "download")

                if "http:" in pdf_url:
                    pdf_url = pdf_url.replace("http:", "https:")

            abstract_url = raw_paper.find("a", href=True)["href"]
            if year < 2019:
                abstract_url = abstract_url.replace("view", "viewPaper")
            abstract_url = abstract_url.replace("http:", "https:")
            abs_src = requests.get(abstract_url).content
            abs_soup = BeautifulSoup(abs_src, "lxml")
            if year == 2019:
                abstract = abs_soup.find("p").text.strip()
            else:
                try:
                    abstract = (
                        abs_soup.find("div", id="abstract").find("div").text.strip()
                    )
                except:
                    print("Failed on abstract {}".format(abstract_url))

            # Unique ID: note 2nd to last numeric is the unique ID, unclear what the final numeric is
            if year == 2019:
                unique_id = pdf_url.split("/")[8]
            else:
                unique_id = pdf_url.split("/")[9]

            path = "./AAAI/" + title + ".pdf"
            try:
                urllib.request.urlretrieve(pdf_url, path)
                # TODO race condition??
                # COLNET ":" to "/" issue
                fp = open(path, "rb")
                paper_text = modules.get_pdf_from_fp(fp)
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
            except Exception as e:
                print("**** PAPER WITH TITLE [{}] FAILED ****".format(title))
                print(e)

        with open("aaai" + str(year) + ".csv", "w") as new_csv:
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
