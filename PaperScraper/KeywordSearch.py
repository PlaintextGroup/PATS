import copy
import pickle
import collections

from matplotlib import pyplot as plt
from matplotlib_venn import venn3, venn3_circles

from ManageDocs import *

plt.figure(figsize=(4, 4))

# papers = get_all_papers(text_substr_len=3000) # full text
# paper_to_code = get_title_to_code_url()
infile = open("papers.p", "rb")
papers = pickle.load(infile)
infile.close()

num_papers = 0
urls = set()

imagenet_set = set()
cifar_set = set()
lsun_set = set()
mnist_set = set()
coco_set = set()

years = [2013, 2014, 2015, 2016, 2017, 2018, 2019]
term_to_counts = collections.defaultdict(lambda: [0 for x in years])
counts = [0 for x in years]
counts_2 = [0 for x in years]
counts_3 = [0 for x in years]
counts_4 = [0 for x in years]
counts_5 = [0 for x in years]

num_tf = 0
num_pyt = 0

for paper in papers:
    if "tensorflow" in paper.paper_text.lower():
        num_tf += 1
    if "pytorch" in paper.paper_text.lower():
        num_pyt += 1

    if "style transfer" in paper.paper_text.lower():
        cifar_set.add(paper.title)
    if "imagenet" in paper.paper_text.lower():
        imagenet_set.add(paper.title)
    if "generative adversarial network" in paper.paper_text.lower():
        mnist_set.add(paper.title)
    if "imagenet" in paper.abstract.lower():
        counts[years.index(int(paper.year))] += 1
    if "cifar" in paper.abstract.lower():
        counts_2[years.index(int(paper.year))] += 1
    if "mnist" in paper.abstract.lower():
        counts_3[years.index(int(paper.year))] += 1
    if "convolutional neural network" in paper.abstract.lower():
        counts_4[years.index(int(paper.year))] += 1
    if "neural network" in paper.abstract.lower():
        counts_5[years.index(int(paper.year))] += 1

print(num_tf, num_pyt)

# plt.plot(years, counts, label='CIFAR')
# plt.plot(years, counts_2, label='ImageNet')
# plt.plot(years, counts_3, label='MNIST')
# plt.plot(years, counts_4, label='CNN')
# plt.plot(years, counts_5, label='NN')
# plt.title("Keyword mentions in papers per year")
# plt.legend()

venn3(
    [cifar_set, imagenet_set, mnist_set],
    set_labels=["Style transfer", "ImageNet", "GANs"],
)

plt.show()

# if 'tensorflow' in paper.abstract.lower() and paper.title in paper_to_code:
# if 'cifar' in paper.abstract.lower():
#     num_papers += 1
#     print(paper.title)
# urls.add(paper_to_code[paper.title])

# print('{}/{}'.format(num_papers, len(papers)))
# print(urls)
# print(len(papers))
