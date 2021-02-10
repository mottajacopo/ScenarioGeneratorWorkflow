import json

#save json file with parameters
data = {}
data["Parameters"] = []

item = {}
item["approachSpeed"] = [10, 20, 30]
item["initialOffset"] = [80, 100]
item["randomPosition"] = [True]
data["Parameters"].append(item)


with open('param.json', 'w') as outfile:
    json.dump(data, outfile)

