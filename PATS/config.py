# if single_institution_analysis is on, make sure to include single_institution_name
# if keyword comparison enabled, add keywords into keywords. comparison is between china and US

citations = {
    # Filters
    "country_analyzed": [],  # leave blank to analyze all
    "years_analyzed": [],  # leave blank to analyze all years from 2013-2019
    "institution_analyzed": [],  # blank for all institutions
    "institution_type_analyzed": [],  # ['Company', 'Academia', 'Government', 'Independent Research'] blank for all institution types
    "institution_type_dependent": False,  # mark true if you want the institution type analyzed to align with the countries
    "institution_type_strict": False,
    "conferences_analyzed": [
        "neurips"
    ],  # ['aaai','CVPR','iclr','icml','neurips'], blank for all confs
    "keywords": [],
    "only_chinese_coauthors": False,
    "n_plotted": 25,
    "min_keyword_count": 2,
    # TODO
    # update chinese coauthor analysis
    # Output Filters
    "plot_data": False,
    "export_csv": False,
    # Summary Analyses
    "analyze_coauthors": False,
    "open_source": False,
    "top_authors": False,
    # Option Flags
    "verbose": True,
    # "top_author_year_exported": '2019' # specify a year in string format eg: '2019', otherwise blank
}

# unique countries available for country analyzed:

# country_options = ['Australia', 'Austria', 'Belgium', 'Brazil', 'Canada',
# 'Chile', 'China', 'Colombia', 'Czechia', 'Denmark', 'Finland', 'France',
# 'Germany', 'Greece', 'Hong Kong', 'Hungary', 'India', 'Iran', 'Ireland',
# 'Israel', 'Italy', 'Japan', 'Lebanon', 'Luxembourg', 'Netherlands',
# 'New Zealand', 'Norway', 'Poland', 'Portugal', 'Qatar', 'Russia',
# 'Singapore', 'South Korea', 'Spain', 'Sweden', 'Switzerland',
# 'Taiwan', 'Turkey', 'UAE', 'UK', 'US', 'Ukraine', 'Uruguay']

# cv growth

# in cv -- only analyze cvpr
