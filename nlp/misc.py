import torch
import time


class ProgressLog:
    """Prints the actual progress, each time after 1 % of the total is
    completed. This is useful for long running tasks on the k8s cluster, as it
    gets logged to stdout and can be viewed with kubectl logs.
    Create an instance with the total number of steps to be
    completed. Call the increase() method each time a step is completed.
    """
    def __init__(self, total):
        self.total = total
        self.interval_milestone = 1
        self.current_count = 0
        self.last_milestone = time.time()


    def increase(self):
        self.current_count += 1
        progress = (self.current_count / self.total) * 100
        if progress >= self.interval_milestone:
            self.interval_milestone += 1
            now = time.time()
            milestone_duration = now - self.last_milestone
            self.last_milestone = now
            milestones_left = 100 - self.interval_milestone
            time_left_s = (milestones_left * milestone_duration)
            print(f"{self.current_count} of {self.total}: "
                  f"{progress:.0f} percent completed. "
                  f"Approx time left: {(time_left_s/60):.0f} min "
                  f"= {(time_left_s/3600):.1f} h.")


def perform_ner(text, ner_pipeline, score_threshold=0.9):
    """Extracts named entities from text with a confidence score above the
    threshold. Returns a tuple of the extracted entities (list of str) and the
    full results of the NER pipeline (list of dicts with keys 'entity_group',
    'score', 'word', 'start', 'end')."""
    
    ner_results = ner_pipeline(text)
    # list of dicts like the following, if ner pipeline was called with
    # aggregation_strategy="simple":
    # [{'entity_group': 'ORG',
    #   'score': 0.9977342,
    #   'word': 'CNN Opinion',
    #   'start': 51,
    #   'end': 62},
    #  {... ]

    # Cast score to float, this is necessary because of encoding issues
    # with MongoDB (maybe json encoder?)
    for element_dict in ner_results:
        element_dict['score'] = float(element_dict['score'])

    entities = [entry['word'] for entry in ner_results
                if entry['score'] > score_threshold]
    return (list(set(entities)), ner_results)


def perform_clf(text, tokenizer, model):
    """Perform classification on text. Returns a tuple of the predicted class
    label (str) and a dictionary of class labels and their respective
    probabilities (dict).
    possible class labels: 'business', 'entertainment', 'health', 'news',
    'politics', 'sport'."""

    # Tokenize input text
    inputs = tokenizer(text, padding=True, truncation=True, max_length=512,
                       return_tensors="pt")

    # Make prediction
    outputs = model(inputs["input_ids"], attention_mask=inputs["attention_mask"])

    # Get predicted class probabilities
    predicted_probabilities = torch.softmax(outputs.logits, dim=1)

    # Get class labels and corresponding probabilities
    class_labels = model.config.id2label.values()
    class_probabilities = predicted_probabilities[0].tolist()  # for batch size 1
    # Cast to python floats, this is necessary because of encoding issues
    # with MongoDB (maybe json encoder?)
    class_probabilities = [float(prob) for prob in class_probabilities]

    # Create a dictionary. Class label keys, values are respective probabilities
    class_probabilities_dict = dict(zip(class_labels, class_probabilities))

    # Find the class label with the highest probability
    predicted_class = max(class_probabilities_dict, key=class_probabilities_dict.get)

    return (predicted_class, class_probabilities_dict)


if '__name__' == '__main__':
    pass