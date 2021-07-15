# NeurIPS webpages that contain paper proceedings from 1987 - 2018 are in the exact same format. This is the scraper.
import PyPDF4
from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import requests
import io
import csv
from ResearchPaper import ResearchPaper

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

class modules:
    staticmethod

    def get_pdf_from_fp(f, remove_newline=True):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = "utf-8"
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        for page in PDFPage.get_pages(
            f,
            pagenos,
            maxpages=maxpages,
            password=password,
            caching=caching,
            check_extractable=True,
        ):
            interpreter.process_page(page)

        text = retstr.getvalue()

        f.close()
        device.close()
        retstr.close()

        # TODO
        text = text.replace("\0", "")
        if remove_newline:
            text = text.replace("\n", " ")  # removes newlines

        return text

    # TODO doesn't work for those autodownload bad boys
    def pdf_string_from_url(pdf_url):
        r = requests.get(pdf_url)
        f = io.BytesIO(r.content)
        return modules.get_pdf_from_fp(f)
