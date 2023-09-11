# http://localhost:5000/

# Standard library imports
import pickle

# Third-party imports
from flask import Flask, render_template, request
import pandas as pd
from pymongo import MongoClient

# Local imports
## None

app = Flask(__name__)

# Connect to MongoDB
MONGODB_HOST = 'mongodb-service' # must fit k8s service name
MONGODB_PORT = 27017
print("Connect to MongoDB.")
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client['news']
collection = db['articles']

# Count all documents in the collection
count_document = collection.count_documents({})

# Count documents in collection where 'author' field is not empty list
# (i.e. where author has been scraped -> "proper" article)
count_proper = collection.count_documents({'authors': {'$ne': []}})

# Query for documents in collection where 'category' field exists
# (i.e. where nlp has been performed)
query = {'category': {'$exists': True}}

# Count number of documents where nlp has been performed
count_nlp = collection.count_documents(query)

# Print statistics
print(f'Number of documents in collection: {count_document}')
print(f'Number of proper articles: {count_proper}')
print(f'Number of nlp worked articles: {count_nlp}')

# Load from MongoDB and convert to pandas DataFrame
collection_list = list(collection.find(query))
df = pd.DataFrame(collection_list)
print('Successfully loaded data from DB and converted to pandas DataFrame.')

# # local dummy data
# Load from nlp_collection_list.pkl
# with open('../data/nlp_collection_list.pkl', 'rb') as f:
#     nlp_collection_list = pickle.load(f)
# df = pd.DataFrame(nlp_collection_list)


@app.route('/')
def index():
    columns = df.columns
    categories = df['category'].unique()
    return render_template('index.html', columns=columns,
                           categories=categories)

@app.route('/update_table', methods=['POST'])
def update_table():
    selected_columns = request.form.getlist('columns')
    selected_category = request.form['category']

    if selected_columns:
        filtered_df = df[selected_columns]
    else:
        filtered_df = df

    if selected_category:
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    return filtered_df.to_html(classes='table table-bordered table-striped',
                               escape=False, index=False)

if __name__ == '__main__':
    app.run(debug=False)


