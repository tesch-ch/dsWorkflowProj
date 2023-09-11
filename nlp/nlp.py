# Standard library imports
import time
import sys

# Third-party imports
import torch # TODO: might remove, transformers sometimes throws warnings?
from transformers import (AutoTokenizer,
                          AutoModelForSequenceClassification,
                          AutoModelForTokenClassification,
                          pipeline)
from pymongo import MongoClient

# Local imports
import misc


# Connect to MongoDB
# MONGODB_HOST = 'localhost'
MONGODB_HOST = 'mongodb-service' # must fit k8s service name
MONGODB_PORT = 27017
print("Connect to MongoDB.")
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client['news']
collection = db['articles']

# Count number of documents in collection where 'category' field is missing
# (i.e. where nlp has not been performed yet) and where the 'authors' field is
# not empty (i.e. "proper" articles, not e.g. weather reports or landing pages)
query = {'category': {'$exists': False}, 'authors': {'$ne': []}}
# query = {'authors': {'$ne': []},}
count = collection.count_documents(query)
print(f'Number of documents to process: {count}')

# Exit if no documents to process
if count < 10:
    print("There are not enough documents (must be at least 10). Exiting.")
    sys.exit(0)

# Init classifier model for inference on article text
# https://huggingface.co/Softechlb/articles_classification
CLF_MODEL_NAME = "Softechlb/articles_classification"
print("Init classifier model.")
clf_tokenizer = AutoTokenizer.from_pretrained(CLF_MODEL_NAME)
clf_model = AutoModelForSequenceClassification.from_pretrained(CLF_MODEL_NAME)

# Init NER model for inference on article title
# https://huggingface.co/dslim/bert-base-NER
NER_MODEL_NAME = "dslim/bert-base-NER"
print("Init NER model.")
ner_tokenizer = AutoTokenizer.from_pretrained(NER_MODEL_NAME)
ner_model = AutoModelForTokenClassification.from_pretrained(NER_MODEL_NAME)
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer,
                        aggregation_strategy="simple")

# Iterate over documents in collection
progress = misc.ProgressLog(count)
error_count = 0
print("Start processing documents.")
start_time = time.time()
for document in collection.find(query):
    
    try:
        # Perform NER on article title
        (entities, entities_all) = misc.perform_ner(document['title'],
                                                    ner_pipeline)
        
        # Perform classification on article text
        (label, labels_all) = misc.perform_clf(document['text'], clf_tokenizer,
                                               clf_model)

        # Update document in collection
        document['entities'] = entities
        document['entities_verbose'] = entities_all
        document['category'] = label
        document['category_verbose'] = labels_all
        collection.update_one({'_id': document['_id']}, {'$set': document})

    except Exception as e:
        error_count += 1
        print(f"\nError no. {error_count} while "
              f"processing document {document['_id']}:\n{e}\n\n")

    # Print progress
    progress.increase()

duration = time.time() - start_time
print(f"\n\nProcessing {count} documents took {duration / 60:.0f} min.\n"
      f"Average time per document: {duration / count:.2f} s.")

# Close connection to mongo db
client.close()