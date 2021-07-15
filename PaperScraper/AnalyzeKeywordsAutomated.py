import nltk
import pandas
import pickle
import re

# Libraries for text preprocessing
# nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer

# nltk.download('wordnet')
from nltk.stem.wordnet import WordNetLemmatizer

from ManageDocs import *

# papers = get_all_papers(text_substr_len=None)
# outfile = open('papers.p','wb')
# pickle.dump(papers,outfile)
# outfile.close()

# infile = open('papers.p','rb')
papers = pandas.read_pickle("papers.p")
print(papers[0])
print(len(papers))
# infile.close()

paper_abstracts = [p.abstract for p in papers]
# Most common words
# print("Most common words: ")
# freq = pandas.Series(' '.join(paper_abstracts).split()).value_counts()[:20]
# print(freq)

# Least common words
# print("Least common words: ")
# freq = pandas.Series(' '.join(paper_abstracts).split()).value_counts()[-20:]
# print(freq)

##Creating a list of stop words and adding custom stopwords
stop_words = set(stopwords.words("english"))

##Creating a list of custom stopwords
new_words = [
    "model",
    "method",
    "result",
    "algorithm",
    "propose",
    "paper",
    "real",
    "world",
    "show",
    "new",
    "state," "art," "machine," "dimensional",
    "high",
    "optimization",
    "data",
    "set",
    "function",
    "convergence",
    "rate",
    "variable",
    "demonstrate",
    "problem",
    "effectiveness",
    "large",
    "scale",
    "experiment",
    "low",
    "rank",
    "outperforms",
    "end",
    "non",
    "widely",
    "used",
    "state",
    "previous",
    "work",
    "proposed",
    "approach",
    "sample",
    "semi",
    "application",
    "order",
    "magnitude",
    "bound",
    "upper" "benchmark",
    "well",
    "known",
    "dataset",
    "art",
    "performance",
    "task",
    "worst",
    "based",
    "task",
    "time",
    "polynomial",
    "recent",
    "year",
    "view",
    "et",
    "al",
    "making",
    "present",
    "novel",
    "special",
    "case",
    "gradient",
    "descent",
    "monte",
    "datasets",
    "theoretical",
    "framework",
    "ground",
    "truth",
    "best",
    "best",
    "knowledge",
    "solution",
    "long",
    "term",
    "improvement",
    "chain",
    "probability",
    "decision",
    "factorization",
    "however",
    "existing",
]
stop_words = stop_words.union(new_words)

# # TODO (annamitchell): LDA model
# # run on abstracts
# # run on full text + abstract


processed_abstracts = []
for i in range(len(paper_abstracts)):
    abstract = paper_abstracts[i]

    # Remove punctuations
    text = re.sub("[^a-zA-Z]", " ", abstract)

    # Convert to lowercase
    text = text.lower()

    # remove tags
    text = re.sub("&lt;/?.*?&gt;", " &lt;&gt; ", text)

    # remove special characters and digits
    text = re.sub("(\\d|\\W)+", " ", text)

    ##Convert to list from string
    text = text.split()

    ##Stemming
    ps = PorterStemmer()
    # Lemmatisation
    lem = WordNetLemmatizer()
    text = [lem.lemmatize(word) for word in text if not word in stop_words]
    text = " ".join(text)
    processed_abstracts.append(text)

print("Example of preprocessed abstract: ")
print(processed_abstracts[0])
print(len(processed_abstracts))


from sklearn.feature_extraction.text import CountVectorizer

# Most frequently occuring words
def get_top_n_words(corpus, n=None):
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:n]


# top_words = get_top_n_words(processed_abstracts, n=100)
# print(top_words)

stop_bigrams = [
    "neural network",
    "machine learning",
    "deep learning",
    "supervised learning",
    "unsupervised learning",
    "network architecture",
    "computational cost",
    "target domain",
    "black box",
    "network architecture",
    "deep network",
    "gaussian process",
    "multi label",
]

# Most frequently occuring Bi-grams
def get_top_n2_words(corpus, n=None):
    vec1 = CountVectorizer(
        ngram_range=(2, 2), max_features=2000, stop_words=stop_words
    ).fit(corpus)
    bag_of_words = vec1.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec1.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)

    output = [i for i in words_freq if i[0] not in stop_bigrams]
    return output[:n]


top2_words = get_top_n2_words(processed_abstracts, n=20)
print(top2_words)

top2_df = pandas.DataFrame(top2_words)
top2_df.columns = ["Bigram", "Frequency"]
print(top2_df)

# Barplot of most freq Bi-grams
import seaborn as sns

sns.set(rc={"figure.figsize": (13, 6)})
h = sns.barplot(x="Bigram", y="Frequency", data=top2_df)
h.set_xticklabels(h.get_xticklabels(), rotation=45)
h.set_title("Most frequent technical topics in paper abstracts by bigram count")
import matplotlib.pyplot as plt

plt.show()
