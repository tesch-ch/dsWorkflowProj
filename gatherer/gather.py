# Standard library imports
import time

# Third-party imports
from pymongo import MongoClient
import newspaper

# Local imports
## none


# MongoDB connection (must fit k8s service name)
# MONGODB_HOST = 'localhost'
MONGODB_HOST = 'mongodb-service'
MONGODB_PORT = 27017


# News outlets to gather articles from
URLS = {
    'bbc': 'http://www.bbc.com/news',
    'cnn': 'http://www.cnn.com',
    'fox': 'http://www.foxnews.com',
}


# Connect to mongo db
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client['news']
collection = db['articles']

# Get URLs of articles already residing in the database
# TODO: This might require a fix if the database gets too big
urls = [article['url'] for article in collection.find({}, { "url": 1, "_id": 0 })]

# Gather articles from news outlets
for outlet, url in URLS.items():
    paper = newspaper.build(url, memoize_articles=False)
    print(outlet)
    for article in paper.articles:
        if article.url not in urls:
            print(article.url)
            # TODO: Implement actual error handling with full traceback logging
            try:
                article.download()
                article.parse()
                data = {
                    'source': outlet,
                    'url': article.url,
                    'title': article.title,
                    'authors': article.authors,
                    'top_image': article.top_image,
                    'text': article.text,
                    'timestamp': int(time.time()),
                }
                collection.insert_one(data)
            except Exception as e:
                print(e)

# Close connection to mongo db
client.close()
