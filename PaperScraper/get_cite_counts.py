import json
import pickle
import subprocess

from ManageDocs import *
from scholar import *

infile = open("papers.p", "rb")
papers = pickle.load(infile)
infile.close()
print("{} papers loaded".format(len(papers)))

paper_to_cite_count = {}

for p in papers:
    title = p.title
    cmd = 'python scholar.py --title-only --phrase "{}"'.format(title)
    print(cmd)
    subproc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line in subproc.stdout.readlines():
        print(line)
        line_s = str(line)
        if "Citations" in line_s and "Citations list" not in line_s:
            paper_to_cite_count[str((p.conference, p.unique_id))] = line_s

    with open("cite_file.txt", "w") as c_file:
        json.dump(paper_to_cite_count, c_file)
