import scholarly

query = "SnapNETS: Automatic Segmentation of Network Sequences with Node Labels"
a = scholarly.search_keyword(query)
for x in a:
    print(x)

# does not work :'(
