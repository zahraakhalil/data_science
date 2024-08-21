import pymongo
import json

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]

with open("Json_Files/articles_2024_8.json", "r", encoding='utf-8') as f:
    data = json.load(f)

with open("Json_Files/articles_2024_7.json", "r", encoding='utf-8') as f:
    data += json.load(f)

with open("Json_Files/articles_2024_6.json", "r", encoding='utf-8') as f:
    data += json.load(f)

with open("Json_Files/articles_2024_5.json", "r", encoding='utf-8') as f:
    data += json.load(f)

with open("Json_Files/articles_2024_4.json", "r", encoding='utf-8') as f:
    data += json.load(f)

with open("Json_Files/articles_2024_3.json", "r", encoding='utf-8') as f:
    data += json.load(f)

collection.insert_many(data)

