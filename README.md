Note: Plaintext AI Text Searcher (PATS) is now archived, but the source code is still available to view in this repository. Plaintext Group was a nonpartisan, technology innovation policy initiative developed by Schmidt Futures. For more information, see https://www.schmidtfutures.com/our-work/plaintext/.

![Primary_1](https://user-images.githubusercontent.com/12788782/120546871-37e97900-c3a5-11eb-8ab5-61a33fd391b6.png)

# Plaintext AI Text Searcher (PATS): The AI Conference Paper Index


## Plaintext AI Text Searcher (PATS) Overview
Plaintext AI Text Searcher (PATS) is a computational system developed to extract bibliometric metadata (institution, country, keywords) from AI research papers published at top conferences, with the goal of providing a nuanced understanding of the state of AI research globally and to guide critical discussion on AI policy. 

The dataset curated by PATS is 50-100x larger than any other dataset of its kind, which previously only consisted of a few hundred papers analyzed manually. Our dataset encompasses every paper published between 2013 - 2019 (19,861 total) from the following top AI conferences:

- Association for the Advancement of Artificial Intelligence (AAAI),
- Conference on Computer Vision and Pattern Recognition (CVPR), 
- International Conference on Learning Representations (ICLR), 
- The International Conference on Machine Learning (ICML), and
- Conference on Neural Information Processing Systems (NeurIPS).

These conferences were used as a quality filter since they are the most prestigious AI conferences by h-index.

### Dataset Summary

The dataset is stored in the [`Data`](./Data) directory and contains the following papers:

| Conference | # of papers |
|------------|-------------|
| AAAI       | 5,280       |
| CVPR       | 5,296       |
| ICLR       | 1,419       |
| ICML       | 3,008       |
| NeurIPS    | 4,858       |
| **Total**  | **19,861**  |

The dataset is scraped from multiple conference websites, and the scraping code is available in the [`PaperScraper`](./PaperScraper) directory. The main entrypoint for scraping, which contains all the links where we scrape from, is [`PaperScraper/Main.py`](./PaperScraper/Main.py).

<hr />

## Table of Contents


* [PATS Set-Up Instructions and Technical Details](#pats-set-up-instructions-and-technical-details)
    * [How do I set up PATS?](#how-do-i-set-up-pats)
* [PATS API Overview](#pats-api-overview)
    * [How to Use PATS](#how-to-use-pats)
    * [File Structure](#file-structure)
        * [Input Filters](#input-filters)
        * [Output Filters](#output-filters)
        * [Summary Analyses](#summary-analyses)
        * [Additional Flags](#additional-flags)
* [PATS Policy Questions and Analysis Introduction](#pats-policy-questions-and-analysis-introduction)
    * [Policy Questions and Analysis Framework](#policy-questions-and-analysis-framework)
    * [Policy Questions and Analysis Examples](#policy-questions-and-analysis-examples)
        * [Identifying Top AI Research Talent](#identifying-top-ai-research-talent)
        * [International AI Research Collaboration](#international-ai-research-collaboration)
* [PATS Limitations](#pats-limitations)
    * [Research Discoverability and Conference Bias](#research-discoverability-and-conference-bias)
    * [Only publicly released AI research is captured.](#only-publicly-released-ai-research-is-captured)
    * [Conferences focus on fundamental research breakthroughs rather than practical applications.](#conferences-focus-on-fundamental-research-breakthroughs-rather-than-practical-applications)
    * [Conference Weighting](#conference-weighting)
    * [Authorship Ordering](#authorship-ordering)
    * [Institutional Tagging](#institutional-tagging)

<hr />

## PATS Set-Up Instructions and Technical Details
### How do I set up PATS?

Make sure you have Python 3.3+ installed, and either follow the Conda or Virtual Environment Setup outlined below.

**Conda**

First, make sure you’ve installed all of the requirements. We would recommend setting up your own Conda environment ([installation instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)), so that you can manage your own dependencies without interfering with any of your other existing packages. You can do this by entering the following in a shell:

```bash
conda create -n pats python=3.7 anaconda
```

Activate the environment using:

```bash
conda activate pats
```

Next, make sure to clone the repo and install requirements here using

```bash
git clone https://github.com/PlaintextGroup/pats
cd pats
pip install -r requirements.txt
```

That’s it, you’re ready to start making some queries using PATS!

**Virtual Environment**

Make sure to clone the repo using:

```bash
git clone https://github.com/PlaintextGroup/pats
cd pats
```

Now, make your virtualenv. In this example, we’ve called it venv.
Then install requirements:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then you should be good to go!


<hr />

## PATS API Overview
### How to Use PATS
As a summary:

Start in the `PATS/` directory.

1. Fill in the required fields within ```config.py```.
2. Select whether you want a plot or not. If you do, make sure to turn ```plot_data``` to True. If you don’t, the required data will be displayed on the Terminal as plaintext output.
3. Select whether you want an exported CSV. If you do, make sure to turn ```export_csv``` to True.
4. Run ```python analyzer.py```.
5. Graphs will be generated if chosen. To re-run, exit out of the graphs and then repeat!


We’ll take a deeper dive analyzing these steps and each of the filters below.

<hr />

### File Structure
First, let’s take a deeper dive into the code to understand exactly what is going on. We’ll go over the relative file structure first to give a better sense of how everything is organized. If we look at the current folder in ```pats/```, we see a mixture of Python scripts, Python notebooks, and folders. We’ll go through the most important ones, which are ```analyzer.py``` and ```config.py```.


```analyzer.py```

This is the primary file that drives much of the analysis. It compiles all the documents, and aferwards, examines the configurations that have been enabled and generates the specific graphs or outputs that have been specified. You will **NOT** have to touch this file to run PATS.

<hr />

```config.py```

**This is the main file you will edit when interacting with PATS.** You will be changing various fields within this in order to create the proper query. This file consists of multiple JSON-like dictionary objects in which various fields are stored. Each field, explained below, can be configured differently in order to get the proper chart that we want.

To start off, we have several filters to narrow down the amount of data that we want analyzed. These are divided between input and output filters. Your input filters will filter what data you want analyzed. Your output filters will filter the format and style of what is output, most commonly either a graph or a csv.

<hr />

#### Input Filters
```country_analyzed``` - Comma separated list of strings specifying which countries are to be compared. This limits outputs to have at least one contributing author from the chosen country/countries (doesn’t ensure that all authors are from the same country). For analysis purposes, if a paper has multinational associations, it will count as a paper with both countries of origin. For example, if a paper has country affiliations of both France and the US, it will be considered both a French and American paper. This filter will be applied across all subsequent queries where a country is mentioned. Leave this empty if you want papers from all countries analyzed. 

**Example 1:** I want to analyze all papers where at least one contributing author is from Germany.

**Input 1:** ```"country_analyzed": ['Germany']```

**Example 2:** I want to analyze all papers where at least one contributing author is either from the US, China, or Germany.

**Input 2:** ```"country_analyzed": ['US', 'China', 'Germany']```

**Example 3:** I want to analyze all papers, regardless of author country affiliation (all countries analyzed).

**Input 3:** ```"country_analyzed": []```

A unique list of all countries that can be analyzed/placed in this list is available at [country_options.csv](country_options.csv).

<hr />

```years_analyzed``` - Comma separated list of integers specifying which years are to be compared. Will be applied across all subsequent queries where a year is mentioned. Leave empty if you want papers from all years analyzed (2013 - 2019).

**Example 1:** I want to analyze all papers from 2013.

**Input 1:** ```"years_analyzed": [2013]```

**Example 2:** I want to analyze all papers coming from 2013 - 2015.

**Input 2:** ```"years_analyzed": [2013, 2014, 2015]```

**Example 3:** I want to analyze all papers from any year in my dataset (2013 - 2019).

**Input 3:** ```"years_analyzed": []```

A unique list of all years that can be analyzed/placed in this list is available at [year_options.csv](year_options.csv). under year options.

<hr />

```institution_analyzed``` - Comma separated list of strings specifying which institutions are to be compared. Similar to other fields, this filters by papers where there is at least one contributing author from the chosen institution (doesn’t ensure that all authors are from the same institution. For analysis purposes, if a paper has multi-institutional associations, it will count as a paper published by all institutions. For example, if a paper has institutional affiliations of both Facebook and Google, it will be considered a paper from both Facebook and Google. This filter will be applied across all subsequent queries where institutions are mentioned. Leave empty if you want papers from all institutions analyzed.

**Example 1:** I want to analyze all papers where at least one contributing author is from Google.

**Input 1:** ```"institution_analyzed": ['Google']```

**Example 2:** I want to analyze all papers where at least one contributing author is either from Google, SenseTime Group Ltd, or the Massachusetts Institute of Technology.

**Input 2:**
```"institution_analyzed": ['Google', 'SenseTime Group Ltd.', 'Massachusetts Institute of Technology']```

**Example 3:** I want to analyze all papers, regardless of author institutional affiliation (all institutions analyzed).

**Input 3:** ```"institution_analyzed": []```

A unique list of all institutions that can be analyzed/placed in this list is available at [institution_options.csv](institution_options.csv). under institution options.

<hr />

```institution_type_analyzed``` - Comma separated list of strings specifying which institution types are to be compared. Similar to other fields, this filters by papers where there is at least one institution type from the chosen paper (doesn’t ensure that all institutions are of the same institution type. For analysis purposes, if a paper has multi-institutional associations, it will count as a paper published by all institution types. For example, if a paper has institutional affiliations of both Company and Academia, it will be considered a paper published by both company and academia. This filter will be applied across all subsequent queries where institutions are mentioned. Leave empty if you want papers from all institution types analyzed.

**Example 1:** I want to analyze all papers where at least one contributing author is from Academia.

**Input 1:** ```"institution_type_analyzed": ['Academia']```

**Example 2:** I want to analyze all papers where at least one contributing author is either from Government, Academia, or an Independent Researcher.

**Input 2:**
```"institution_type_analyzed": ['Government', 'Academia', 'Independent Research']```

**Example 3:** I want to analyze all papers, regardless of author institutional type affiliation (all institution types analyzed).

**Input 3:** ```"institution_type_analyzed": []```

A unique list of all institution types that can be analyzed/placed in this list is available at [institution_type_options.csv](institution_type_options.csv).

<hr />

```institution_type_dependent``` - This will be a boolean that says I want my institution types to be dependent upon the countries that I have selected. This allows me to be more specific as to how I want my countries and papers to be filtered. Whereas before if we specified in ```institution_type_analyzed``` what we wanted, the filter would be applied to all listed countries. However, this filter allows for greater precision by filtering each country by its specified institution type. This requires the length of the country to be the same length as the institution type, otherwise the program will exit. ```institution_type_analyzed``` must also be specified in the correct order corresponding to whatever needs to be analyzed.

**Example 1:** I want to analyze all US academic papers vs Chinese company papers.

**Input 1:**
```"country_analyzed": ['US', 'China'],```
```"institution_type_analyzed": ['Academia', 'Company'],```
```"institution_type_dependent": True```

**Example 2:** I want to analyze US academic papers, Chinese Government papers, and Brazilian Company Papers.

**Input 2:**
```"country_analyzed": ['US', 'China', 'Brazil'],```
```"institution_type_analyzed": ['Academia', 'Government', 'Company'],```
```"institution_type_dependent": True```

**Example 3:** I want to analyze academic and company papers from both US and China

**Input 3:**
```"country_analyzed": ['US', 'China'],```
```"institution_type_analyzed": ['Company', 'Academia'],```
```"institution_type_dependent": False```

A unique list of all institution types that can be analyzed/placed in this list is available at [institution_type_options.csv](institution_type_options.csv).

<hr />

```conferences_analyzed``` - Comma separated list of lowercase strings specifying which conferences are to be compared. Will be applied across all subsequent queries where conferences are mentioned. Leave empty if you want papers from all conferences analyzed.

**Example 1:** I want to analyze all papers from ICML.

**Input 1:** ```"conferences_analyzed": ['icml']```

**Example 2:** I want to analyze all papers coming from ICML, CVPR, and NeuRIPS.

**Input 2:** ```"conferences_analyzed": ['icml', 'cvpr', 'neurips']```

**Example 3:** I want to analyze all papers from all conferences.

**Input 3:** ```"conferences_analyzed": []```

A unique list of all conferences that can be analyzed/placed in this list is available at [conference_options.csv](conference_options.csv).

<hr />

```keywords/min_keyword_count``` - An array taking in strings with keywords specified. It will search through the paper text using exact string matching and return the papers that fulfill all the keywords required. The minimum keyword count is set in ```min_keyword_count``` and is defaulted to a value of 5, meaning that the word must appear for a minimum of 5 times in order to be filtered in the final dataframe.

**Example 1: ** I want to analyze all papers that mention the word 'education' at least 5 times.

**Input 1: **
```"keywords": ['education'],```
```"min_keyword_count": 5```

**Example 2:** I want to analyze all papers that mention the words 'education', 'writing', AND 'essays' at least 10 times.

**Input 2:** 
```"keywords": ['education', 'writing', 'essays'],```
```"min_keyword_count": 10```

**Example 3:** I want to analyze all papers without specifying for any keywords.

**Input 3:**
```"keywords": [],```
```"min_keyword_count": 5 # default value```

<hr />

```n_plotted``` - Default number of items plotted when no other filters are specified. For example, if all countries are analyzed and a graph is generated, only the top n_plotted lines will show up on the graphs in order to reduce the amount of clutter and highlight the most important data. This value is defaulted to 5.

<hr />

#### Output Filters
Default filters will generate a textual summary of the data in terms of paper titles, which will be displayed in the Terminal. You may configure the following output filters to either generate an output CSV file (with the printed data on the Terminal) or a plot.

```plot_data``` - Given the filters selected above, this will generate TWO graphs (Figure 1 and FIgure 2) of the number of papers output by year as well as the outputs by institution. Primary graphical output includes graphing an analysis of the number of papers published by institution AND country selected per year. For example, Figure 1 will be your graph by country, and Figure 2 will be the top institutions for the country/countries selected. 

**Example 1:** I want to plot out all papers where at least one contributing author is from Google from years 2013 - 2019.

**Input 1:** 
```"institution_analyzed": ['Google'],```
``` "years_analyzed": [],```
``` "plot_data": True```

**Example 2:** I want to plot out all papers where at least one contributing author is from the US or China from years 2013 - 2019.

**Input 2:** 
```"country_analyzed": ['US', 'China'],```
``` "years_analyzed": [],```
``` "plot_data": True```

**Example 3:** I only want papers where at least one contributing author is from Google from years 2013 - 2019.

**Input 3:** 
```"institution_analyzed": ['Google'],```
``` "years_analyzed": [],```
``` "plot_data": False```

<hr />

```export_csv``` - Exports a csv of the final dataframe with the title of the paper as well as the year. Same data as above with plotting the data, except instead a CSV is exported. To read the full text of the paper, simply search for the title of the paper and you will receive the full text. CSV exports do not contain full text in order to conserve memory.

**Example 1:** I want to export a CSV with all papers where at least one contributing author is from Google from years 2013 - 2019.

**Input 1: **
```"institution_analyzed": ['Google']```
``` "years_analyzed": [],```
``` "export_csv": True```

<hr />

#### Summary Analyses
The summary analyses are preset summaries that can be printed in case you are curious about different varying summary statistics.
analyze_coauthors - Graphs the amount of co-authors per paper from the filtered dataframe. For example, if a paper has two authors, then the number of papers with 2 authors will go up by 1. If there is 1 author, then the number of papers with 1 author will be incremented by 1.
top_authors - Displays the top authors from the filtered dataframe, sorted in reverse order starting with the most publications over the selected year range.

<hr />

#### Additional Flags
```verbose``` - Enables all print statement details to be enabled when switched to True. Also will print out summary statistics by conference and other miscellaneous summaries.

<hr />

## PATS Policy Questions and Analysis Introduction
Now that you’re familiar with how to set up PATS, let’s revisit our main goal of bolstering tech policy findings — the data provided by PATS provides an invaluable starting point when guiding critical discussion on AI policy. 

### Policy Questions and Analysis Framework
In this section, we outline a potential policy framework you may find useful to help guide discussions.

**Overarching Question:** What is the main policy concept we want to explore?

**Sub-Question:** Are there further subdivisions of the Overarching Question?
1. **Main Question(s):** What are the main questions within this topic area? 
2. **Customer:** Who is a (potential) customer?
3. **PATS Query:** What is the query that needs to be inputted into PATS to answer the question? 
4. **Other potential use cases:** Other questions/queries that can be answered using PATS.

<hr />

### Policy Questions and Analysis Examples

#### Identifying Top AI Research Talent 
**Overarching Question(s):** As a funder, how can I identify top AI Research Talent in a more effective and efficient manner than just simply using our networks and press?

**Sub-Question:** Can I identifying top AI Researchers by topic?
1. **Main Question(s):** Who are the top AI researchers working on ```[insert topic]```? What are potential strategies to involve them in our talent programs? 
2. **Customer:** Large Funding Agency (NSF, NASA, NIH), Philanthropic Funders (Schmidt Futures, CZI), Press (NYT, Politico)
3. **PATS Query:** Filter by ```[YOUR_TOPIC_HERE]```, and then rank authors in descending order. You can also filter how many times you want the word to appear.

**Example:**
```"keywords": ['YOUR_TOPIC_HERE'],```
```"min_keyword_count": 5, # default ```
```"export_csv": True```

4. **Other potential use cases:** Finding nominators for talent programs, inviting potentially lesser-known academics to competitions, sourcing of domain experts for opinions and dialogue, grant making use (who are the top performers?), policy making (who is contributing on a global stage? Potential interview to bring new insights to different AI commissions).


#### International AI Research Collaboration
**Overarching Question(s):** How much international academic collaboration is occurring in AI? How much does the US work with China?

**Sub-Question:** How much do other countries work together? 

1. **Main Question(s):**  How much is the US collaborating with other countries?
2. **Customer:** Press, AI Commissions, other interested parties
3. **PATS Query:** Filter papers by academic institutions and ‘US’

**Example:**
```"country_analyzed": ['US'],```
```"institution_type_analyzed": ['Academia'],```
```"export_csv": True```

4. **Other potential use cases:** Recruitment internal/external talent programs both internationally and domestically.

<hr />

## PATS Limitations

While PATS performs at a high-level to accomplish given tasks, there are still certain limitations that present itself as future improvements. More specifically, we are limited by research discoverability and conference weighting among others.

### Research Discoverability and Conference Bias
While we have created a large corpus of papers, we primarily are limited by the amount of conferences that we currently scrape. We have to introduce newer scripts in order to scrape other more specific conferences to get more domain targeted papers such as specific conferences for a chosen topic (Association of Computational Linguistics for AI + Education). Lastly, since many of these top AI conferences are US based, there is inherent bias for US authors. This can be accounted for by analyzing more conferences.


### Only publicly released AI research is captured. 
In addition, we struggle with gauging research out of the public eye, such as private company research. While we have tried to expand PATS to account for this, it is hard to find high-integrity qualitative research indicators outside of academic conferences. Including pre-prints and abstracts may increase the amount of material analyzed, but this subset of writing is often of a lower-tier since they have not been peer-reviewed. As a result, this could decrease the signal to noise ratio in terms of quality publications, but could be an avenue to explore in order to better understand the other types of research happening.


### Conferences focus on fundamental research breakthroughs rather than practical applications.
Because the accepted papers into these conferences are typically associated with fundamental research, PATS does not allow prediction on which research methods mentioned in these papers will eventually lead to more impactful real-world applications. 


### Conference Weighting
Currently, all conferences are given equal weighting although some researchers may prioritize some over the other. For example, NeurIPS and ICML are historically regarded as the premier academic conference for submission, while the others, such as AAAI and CVPR, act as niche conferences with specific focuses within AI and Machine Learning that are typically less prestigious. Assigning equal weighting to these conferences can sometimes diminish the value of publications, but this can be alleviated when specifically looking at certain conferences. 

### Authorship Ordering
PATS currently doesn’t support analysis of authorship ordering. Since academic papers often have authors listed in terms of authorship contributions, it can be important to track authorship order in order to determine which of the authors are contributing the most. However, one finer nuance to note is that oftentimes primary principal investigators (PIs) are often listed at the end of the list.

### Institutional Tagging
Our institutional tagging is currently limited by spreadsheet entries that map certain countries with institutions. This needs to be maintained otherwise for newer conferences, it will not work as well. 

