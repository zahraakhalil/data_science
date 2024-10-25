import stanza
from pymongo import MongoClient
from textblob import TextBlob
from deep_translator import GoogleTranslator

client = MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]

stanza.download('ar')
nlp = stanza.Pipeline('ar')

def get_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({"entity": ent.text, "label": ent.type})  # Use ent.type for Stanza entity labels

    print(f"---------------------------------\nEntities: {entities}\n---------------------------------")
    return entities


count = 0
for doc in collection.find()[:200]:
    count += 1
    print(f"{count}- Title: \"{doc.get('title')}\"")

    # Check if the 'entities' field is already present or empty
    entities = doc.get("entities", None)
    if not entities:  # If 'entities' is None or empty, process the text
        text = doc.get("content", "")
        if text:  # Only process if there is actual text
            entities = get_entities(text)
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"entities": entities}}
            )


def analyze_sentiment(text):
    try:
        translated_text = GoogleTranslator(source='ar', target='en').translate(text)
        blob = TextBlob(translated_text)

        polarity = blob.sentiment.polarity

        if polarity > 0:
            sentiment = "Positive"
        elif polarity < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        return (sentiment, polarity)

    except Exception as e:
        print(f"An error occurred: {e}")
        # Return a neutral sentiment and zero polarity on error
        return ("Neutral",  0.0)


for doc in collection.find()[:200]:
    text = doc.get("content", "")
    overall_sentiment, polarity = analyze_sentiment(text)
    print(f'Title: {doc.get("title")} : {overall_sentiment}')

    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"sentiment": overall_sentiment, "polarity": polarity}}
    )

