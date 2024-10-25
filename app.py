from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]


@app.route("/top_keywords", methods=["GET"])
def top_keywords():
    pipeline = [
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("top_keyword.html", results=result)


@app.route("/top_authors", methods=["GET"])
def top_authors():
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("top_author.html", results=result)


@app.route("/articles_by_date", methods=["GET"])
def articles_by_date():
    pipeline = [
        {"$project": {"publication_date": {"$dateFromString": {"dateString": "$publication_date"}}}},
        {"$project": {"publication_date": {
                "$dateFromParts": {
                    "year": {"$year": "$publication_date"},
                    "month": {"$month": "$publication_date"},
                    "day": {"$dayOfMonth": "$publication_date"}
                }}}},
        {"$group": {"_id": "$publication_date", "count": {"$sum": 1}}},
        {"$sort": {"_id": -1}}]

    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_date.html", results=result)


@app.route("/articles_by_word_count", methods=["GET"])
def articles_by_word_count():
    pipeline = [
        {"$project": {"word_count": {"$toInt": "$word_count"}}},
        {"$group": {"_id": "$word_count", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 30},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_word_count.html", results=result)


@app.route("/articles_by_language", methods=["GET"])
def articles_by_language():
    pipeline = [
        {"$group": {"_id": "$lang", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_language.html", results=result)


@app.route("/articles_by_classes", methods=["GET"])
def articles_by_classes():
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.mapping": "category"}},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_classes.html", results=result)


@app.route("/recent_articles", methods=["GET"])
def recent_articles():
    pipeline = [
        {"$project": {"publication_date": 1, "title": 1, "url": 1, "_id": 0}},
        {"$sort": {"publication_date": -1}},
        {"$limit": 10}
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("recent_articles.html", results=result)


@app.route("/articles_by_keyword/<keyword>", methods=["GET"])
def articles_by_keyword(keyword):
    pipeline = [
        {"$unwind": "$keywords"},
        {"$match": {"keywords": keyword}},
        {"$project": {"_id": 0, "title": 1, "keywords": 1, "word_count": 1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_keyword.html",results=result)


@app.route("/articles_by_author/<author_name>", methods=["GET"])
def articles_by_author(author_name):
    pipeline = [
        {"$match": {"author": author_name}},
        {"$project": {"_id": 0, "title": 1, "publication_date": 1}},
        {"$sort": {"publication_date": -1}},
        {"$limit": 20}
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_author.html", results=result)


@app.route("/top_classes", methods=["GET"])
def top_classes():
    pipeline = [
        {"$unwind": "$classes"},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("top_classes.html", results=result)


@app.route("/article_details/<postid>", methods=["GET"])
def article_details(postid):

    pipeline = [
        {"$match": {"postid": postid}},
        {"$project": {"_id": 0, "postid": 1, "publication_date": 1, "title": 1, "keywords": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("article_detail.html", results=result)


@app.route("/articles_with_video", methods=["GET"])
def articles_with_video():
    pipeline = [
        {"$match": {"video_duration": {"$ne": None}}},
        {"$project": {"_id": 0}},
    ]
    result = list(collection.aggregate(pipeline))
    new_result = [{"id": "Article With Video", "count": len(result)}, {"id": "Article without Video",
                                                                       "count": 10000-len(result)}]
    return render_template("artcles_with_videos.html", results=new_result)


@app.route("/articles_by_year", methods=["GET"])
def articles_by_year():
    pipeline = [
        {"$project": {"_id": 0, "publication_date": {"$dateFromString": {"dateString": "$publication_date"}}}},
        {"$project": {"publication_date": {"$toInt": {"$dateToString": {"format": "%Y",
                                                                        "date": "$publication_date"}}}}},
        {"$group": {"_id": "$publication_date", "count": {"$sum": 1}}}
    ]
    results = list(collection.aggregate(pipeline))
    new_result = list()
    for result in results:
        new_result.append({"Year": f"{result['_id']}", "count": result["count"]})
    return render_template("articles_by_year.html", results=new_result)


@app.route("/longest_articles", methods=["GET"])
def longest_articles():
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "word_count": {"$toInt": "$word_count"},
            }
        },
        {"$sort": {"word_count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("longest_article.html", results=result)


@app.route("/shortest_articles", methods=["GET"])
def shortest_articles():
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "word_count": {"$toInt": "$word_count"},
            }
        },
        {"$sort": {"word_count": 1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("shortest_articles.html", results=result)


@app.route("/articles_by_keyword_count", methods=["GET"])
def articles_by_keyword_count():
    pipeline = [
        {
            "$project": {
                "keywords_count": {"$size": "$keywords"},
            }
        },
        {"$group": {"_id": "$keywords_count", "articles_count": {"$sum": 1}}},
        {"$sort": {"articles_count": 1}},
        {"$project": {
            "keyword_number": "$_id",
            "_id": 0,
            "articles_count": 1
        }}
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_keyword_count.html", results=result)


@app.route("/articles_with_thumbnail", methods=["GET"])
def articles_with_thumbnail():
    pipeline = [
        {"$match": {"thumbnail": {"$ne": None}}},
        {"$project": {"_id": 0, "title": 1, "thumbnail": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    new_result = [{"id": "Articles with Thumbnail", "count": len(result)},
                  {"id": "Articles without Thumbnail", "count": 10000-len(result)}]
    return render_template("articles_with_thumbnail.html", results=new_result)


@app.route("/articles_updated_after_publication", methods=["GET"])
def articles_updated_after_publication():
    pipeline = [
        {"$match": {"$expr": {"$gt": ["$last_updated_date", "$publication_date"]}}},
        {"$project": {"_id": 0, "title": 1,
            "published_time": {
                "$dateFromString": {"dateString": "$publication_date"}
            },
            "last_updated": {"$dateFromString": {"dateString": "$last_updated_date"}},
        }
        },
    ]
    result = list(collection.aggregate(pipeline))
    new_results = [{"id": "Articles Updated", "count": len(result)},
                   {"id": "Articles Not Updated", "count": 10000-len(result)}]
    return render_template("articles_updated_after_publication.html", results=new_results)


@app.route("/articles_by_coverage/<coverage>", methods=["GET"])
def articles_by_coverage(coverage):
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.mapping": "coverage"}},
        {"$project": {"_id": 0, "title": 1, "author": 1, "classes": 1}},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_coverage.html", results=result)


@app.route("/popular_keywords_last_X_days", methods=["GET"])
def popular_keywords_last_X_days():
    days = 7
    date_X_days_ago = datetime.utcnow() - timedelta(days=days)
    print(date_X_days_ago)
    pipeline = [
        {
            "$project": {
                "published_time": {
                    "$dateFromString": {"dateString": "$published_time"}
                },
                "_id": 0,
            }
        },
        {"$match": {"published_time": {"$gte": date_X_days_ago}}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


@app.route("/articles_by_month/<int:year>/<int:month>", methods=["GET"])
def articles_by_month(year, month):
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "published_time": {
                    "$dateFromString": {"dateString": "$published_time"}
                },
            }
        },
        {
            "$match": {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$year": "$published_time"}, year]},
                        {"$eq": [{"$month": "$published_time"}, month]},
                    ]
                }
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


@app.route("/articles_by_word_count_range/<int:min>/<int:max>", methods=["GET"])
def articles_by_word_count_range(miin, maxx):
    pipeline = [
        {"$project": {"_id": 0, "title": 1, "word_count": {"$toInt": "$word_count"}}},
        {
            "$match": {
                "$and": [{"word_count": {"$gte": miin, "$lte": maxx}}]
            }
        },
        {"$sort": {"word_count": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    new_result = [{"id": f"Articles between {miin} and {maxx} words", "count": len(result)},
                  {"id": "Other Articles", "count": 10000-len(result)}]
    return render_template("articles_by_word_count_range.html", results=new_result)


@app.route("/articles_with_specific_keyword_count/<int:count>", methods=["GET"])
def articles_with_specific_keyword_count(count):
    pipeline = [
        {"$project": {"_id": 0, "title": 1, "keywords_count": {"$size": "$keywords"}}},
        {"$match": {"keywords_count": count}},
    ]
    result = list(collection.aggregate(pipeline))
    new_result = [{"id": f"Articles That have {count} keywords", "count": len(result)},
                  {"id": "Other Articles", "count": 10000 - len(result)}]
    return render_template("articles_with_specific_keyword_count.html", results=new_result)


@app.route("/articles_by_specific_date/<date>", methods=["GET"])
def articles_by_specific_date(date):
    date_format = "%Y-%m-%d"
    date = str(datetime.strptime(date, date_format).date())
    pipeline = [
        {
            "$project": {
                "_id": 0, "title":1,
                "published_time": {
                    "$dateFromString": {"dateString": "$publication_date"}
                },
            }
        },
        {
            "$match": {
                "$expr": {
                    "$eq": [
                        {
                            "$dateToString": {
                                "date": "$published_time",
                                "format": date_format,
                            }
                        },
                        date,
                    ]
                }
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_specific_date.html", results=result)


@app.route("/articles_containing_text/<text>", methods=["GET"])
def articles_containing_text(text):

    pipeline = [
        {"$match": {"content": {"$regex": text, "$options": "i"}}},
        {"$project": {"_id": 0, "title": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    new_result = [{"id": f"Articles That have inside its content {text}", "count": len(result)},
                  {"id": "Other Articles", "count": 10000 - len(result)}]
    return render_template("articles_containing_text.html", results=new_result, k=text)


@app.route("/articles_with_more_than/<int:word_count>", methods=["GET"])
def articles_with_more_than(word_count):
    pipeline = [
        {"$project": {"_id": 0, "title": 1, "word_count": {"$toInt": "$word_count"}}},
        {"$match": {"word_count": {"$gte": word_count}}},
        {"$sort": {"word_count": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    new_result = [{"id": f"Articles with More Than {word_count} Word", "count": len(result)},
                  {"id": f"Articles with Less Than {word_count} Word", "count": 10000 - len(result)}]
    return render_template("articles_with_more_than.html", results=new_result, k=word_count)


@app.route("/articles_grouped_by_coverage", methods=["GET"])
def articles_grouped_by_coverage():
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.mapping": "coverage"}},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": 1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_grouped_by_coverage.html", results=result)


@app.route("/articles_last_X_hours", methods=["GET"])
def articles_last_X_hours():
    hours = 24
    date_X_hours_ago = datetime.utcnow() - timedelta(hours=hours)
    pipeline = [
        {
            "$project": {
                "published_time": {
                    "$dateFromString": {"dateString": "$published_time"}
                },
                "_id": 0,
            }
        },
        {"$match": {"published_time": {"$gte": date_X_hours_ago}}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


@app.route("/articles_by_title_length", methods=["GET"])
def articles_by_title_length():
    pipeline = [
        {"$group": {"_id": {"$strLenCP": "$title"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 30}
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("articles_by_title_length.html", results=result)

@app.route("/sentiment_trends", methods=["GET"])
def sentiment_trends():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "sentiment": "$sentiment",
                    "year": {
                        "$year": {"$dateFromString": {"dateString": "$publication_date"}}
                    },
                    "month": {
                        "$month": {"$dateFromString": {"dateString": "$publication_date"}}
                    },
                },
                "count": {"$sum": 1},
            }
        },
        {
            "$project": {
                "sentiment": "$_id.sentiment",
                "year": "$_id.year",
                "month": "$_id.month",
                "count": 1,
                "_id": 0,
            }
        },
        {"$sort": {"year": 1, "month": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("sentiment_trends.html", results=result)

@app.route("/most_positive_articles", methods=["GET"])
def most_positive_articles():
    pipeline = [
        {"$sort": {"polarity": -1}},
        {"$project": {"_id": 0, "title": 1, "polarity": 1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("most_positive_articles.html", results=result)


@app.route("/most_negative_articles", methods=["GET"])
def most_negative_articles():
    pipeline = [
        {"$sort": {"polarity": 1}},
        {"$project": {"_id": 0, "title": 1, "polarity": 1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("most_negative_articles.html", results=result)

@app.route("/top_entities", methods=["GET"])
def top_entities():
    pipeline = [
        {"$unwind": "$entities"},
        {"$group": {"_id": "$entities.entity", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]
    result = list(collection.aggregate(pipeline))
    return render_template("top_entities.html", results=result)


if __name__ == "__main__":
    app.run(debug=True)
