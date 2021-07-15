from PyPDF4 import PdfFileReader
from bs4 import BeautifulSoup
import urllib
import requests
import io
import csv
from ResearchPaper import ResearchPaper

path = "./AAAI/Improving One-Class Collaborative Filtering via Ranking-Based Implicit Regularizer.pdf"

reader = PdfFileReader(path)
num_pages = reader.numPages
count = 0
paper_text = ""

while count < num_pages:
    pageObj = reader.getPage(count)
    count += 1
    paper_text += pageObj.extractText()

print(paper_text)
