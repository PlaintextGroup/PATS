import csv
import matplotlib.pyplot as plt
from statistics import stdev

years = ["2013", "2014", "2015", "2016", "2017", "2018", "2019"]
with open("../Data/AI_Conferences/top_authors.csv", "r") as affil_csv:
    csv_reader = csv.reader(affil_csv)
    header = [
        "author",
        "paper_count",
        "institution",
        "2013",
        "2014",
        "2015",
        "2016",
        "2017",
        "2018",
        "2019",
        "Notes",
    ]
    next(csv_reader)  # skip header

    x_vals = []
    y_vals = []
    for idx, row in enumerate(csv_reader):
        # if idx > 10: break
        # print(row)
        x_vals.append([2013, 2014, 2015, 2016, 2017, 2018])
        new_y = []
        for count in row[3:-1]:
            new_y.append(int(count))
        y_vals.append(new_y)

    y_vals.sort(key=lambda x: -x[5])
    # y_vals.sort(key=lambda x: -stdev(x)) # just kinda interesting

    for idx, (x_dat, y_dat) in enumerate(zip(x_vals, y_vals)):
        if idx > 15:
            break
        plt.plot(x_dat, y_dat)
    plt.title(
        "Papers per year for top 15 authors by 2018 all conference publication count"
    )
    plt.show()

    # print(x_vals)
    # print(y_vals)
