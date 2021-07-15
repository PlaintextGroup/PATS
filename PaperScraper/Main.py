import sys

from OldNeruIPSScraper import OldNeurIPSScraper
from ICMLScraper import ICMLScraper
from AAAIScraper import AAAIScraper
from ICLR2018PlusScraper import ICLR2018PlusScraper
from ICLR20152016Scraper import ICLR20152016Scraper
from ICLR2017Scraper import ICLR2017Scraper
from ICLR20132014Scraper import ICLR20132014Scraper
from NeurIPS2019Scraper import NeurIPS2019Scraper
from Modules import modules

icml_year_to_url = {
    2019: "http://proceedings.mlr.press/v97/",
    2018: "http://proceedings.mlr.press/v80/",
    2017: "http://proceedings.mlr.press/v70/",
    2016: "http://proceedings.mlr.press/v48/",
    2015: "http://proceedings.mlr.press/v37/",
    2014: "http://proceedings.mlr.press/v32/",
    2013: "http://proceedings.mlr.press/v28/",
}

num_args = len(sys.argv)
if num_args == 3:
    # script name, conference, year
    # have: ICML 2013-2019, ICLR 2017
    conference = sys.argv[1].lower()
    year = int(sys.argv[2])
    print("Conference = [{}]; year = [{}]".format(conference, year))
    if conference == "icml":
        if year >= 2013 and year <= 2019:
            print("ICML scraper 2013-2019 for {}".format(year))
            ICMLScraper.scrape_icml(icml_year_to_url[year], year)
    elif conference == "neurips":
        if year < 2019 or True:
            num_2018 = 31
            # TODO could change NeurIPS number in the URL, but seems to work without this
            OldNeurIPSScraper.scrape_old_neurips(
                "http://papers.nips.cc/book/advances-in-neural-information-processing-systems-31-{}".format(
                    year
                ),
                year,
            )
        else:
            NeurIPS2019Scraper.scrape_neurips_2019(
                "https://nips.cc/Conferences/2019/AcceptedPapersInitial", year
            )
        # TODO build NeurIPS scraper
    elif conference == "iclr":
        if year == 2013 or year == 2014:
            print("ICLR 2013 2014 scraper for {}".format(year))
            ICLR20132014Scraper.scrape_iclr_2013_2014(
                "https://iclr.cc/archive/www/doku.php%3Fid=iclr{}:accepted-main.html".format(
                    year
                ),
                year,
            )
        elif year == 2015 or year == 2016:
            print("ICLR 2015 2016 scraper for {}".format(year))
            ICLR20152016Scraper.scrape_iclr_2015_2016(
                "https://iclr.cc/archive/www/doku.php%3Fid=iclr{}:accepted-main.html".format(
                    year
                ),
                year,
            )
        elif year == 2017:
            print("ICLR scraper 2017")
            ICLR2017Scraper.scrape_iclr_2017(
                "https://openreview.net/group?id=ICLR.cc/2017/conference", 2017
            )
        elif year == 2018 or year == 2019:
            print("ICLR scraper 2018 2019 for {}".format(year))
            ICLR2018PlusScraper.scrape_iclr_2018_plus(
                "https://iclr.cc/Conferences/{}/Schedule?type=Poster".format(year), year
            )
        else:
            print("ICLR scrapers do not support this year :'(")
    elif conference == "aaai":
        year_lasttwo = year % 100
        print("AAAI scraper, for {}".format(year_lasttwo))
        AAAIScraper.scrape_aaai(
            "https://www.aaai.org/Library/AAAI/aaai{}contents.php".format(year_lasttwo),
            year,
        )
else:
    print("Not doing specific conference")
    # ICMLScraper.scrape_icml("http://proceedings.mlr.press/v97/", 2019)
    # ICMLScraper.scrape_icml("http://proceedings.mlr.press/v80/", 2018)
    # ICMLScraper.scrape_icml("http://proceedings.mlr.press/v70/", 2017)
    # ICMLScraper.scrape_icml("http://proceedings.mlr.press/v48/", 2016)
    # ICMLScraper.scrape_icml("http://proceedings.mlr.press/v37/", 2015)
    # ICMLScraper.scrape_icml("http://proceedings.mlr.press/v32/", 2014)
    # ICMLScraper.scrape_icml("http://proceedings.mlr.press/v28/", 2013)
    # TODO ICML 2012 has a different format, we omit because it happened (July) before AlexNet (Sept)?

    # TODO ICLR 2013 (first year)
    # TODO ICLR 2014
    # ICLR20152016Scraper.scrape_iclr_2015_2016("https://iclr.cc/archive/www/doku.php%3Fid=iclr2015:accepted-main.html", 2015)

    # TODO debug issue with ICLR 2016, new author tag schema
    # ICLR20152016Scraper.scrape_iclr_2015_2016("https://iclr.cc/archive/www/doku.php%3Fid=iclr2016:accepted-main.html", 2016)
    # TODO ICLR 2017 is different
    # ICLR2017Scraper.scrape_iclr_2017("https://openreview.net/group?id=ICLR.cc/2017/conference", 2017)
    # ICLR2018PlusScraper.scrape_iclr_2018_plus("https://iclr.cc/Conferences/2018/Schedule?type=Poster", 2018)
    # ICLR2018PlusScraper.scrape_iclr_2018_plus("https://iclr.cc/Conferences/2019/Schedule?type=Poster", 2019)

    # TODO AAAI SCRAPER STILL CAN'T GET PDF TEXT

    # OldNeurIPSScraper.scrape_old_neurips("http://papers.nips.cc/book/advances-in-neural-information-processing-systems-31-2018", 2018)

    # TODO build NeurIPS 2019 / some ICLR also in that nice new format?
