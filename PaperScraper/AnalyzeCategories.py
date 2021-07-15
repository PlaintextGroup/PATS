import pickle
from ManageDocs import *

infile = open("papers.p", "rb")
papers = pickle.load(infile)
infile.close()

split_papers = get_papers_without_references(papers)

for p in split_papers:
    title = p.title
