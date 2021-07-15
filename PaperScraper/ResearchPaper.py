class ResearchPaper:
    def __init__(
        self,
        unique_id,
        year,
        title,
        pdf_url,
        authors,
        paper_text,
        abstract="",
        conference="",
    ):
        # easy to scrape
        self.unique_id = unique_id
        self.year = year
        self.title = title
        self.pdf_url = pdf_url
        self.authors = authors
        self.paper_text = paper_text
        self.abstract = abstract
        self.conference = conference

        # add later
        # self.oral_preso
        # self.institution

    def display_paper(self):
        print("ID: ", self.unique_id)
        print("Year: ", self.year)
        print("Title: ", self.title)
        print("PDF URL: ", self.pdf_url)
        print("Authors: : ", self.authors)
        # print("Paper Text: ", self.paper_text)
