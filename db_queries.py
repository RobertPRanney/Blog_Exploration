from pymongo import MongoClient

client = MongoClient()

db = client['data_science_blogs']
table = db['blogs']

test = table.findOne()
print test.keys()


test = table.find()
all_keys = [dct.keys() for dct in test]


df = pd.DataFrame(list(table.find()))
