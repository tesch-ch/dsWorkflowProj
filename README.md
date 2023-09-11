# dsWorkflowProj

This project realizes a very basic newsreader app utilizing a microservices architecture.
The news outlets BBC, CNN and Foxnews are scraped for articles, which are stored into a MongoDB.
On said articles two nlp tasks are performed (classification into news categories and named entity recognition).
Users can access and browse the processed articles through a web app.
 

## Basic Structure
[]



## Ideas/discussion
- batch processing for parallel processing 
- batch processing gpu usage...
- "back to the roots", keep it simple, working with old python versions, no type hinting...
- postprocessing unique named entities etc...
- Encoding issues had to be fixed (Encoding issue: cannot encode object: 0.78782666, of type: <class 'numpy.float32'>)
- use tqdm...
- UnicodeEncodeError: 'ascii' codec can't encode character '\u2019' in position 58: ordinal not in range(128)
- Suddenly no more pod logs visible (solution set ENV PYTHONUNBUFFERED=1)