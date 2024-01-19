import json
import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
import tflearn

""" 
Model that can classify text into different categories
"""



# Initialize stemmer
stemmer = LancasterStemmer()
debug = True
# Load data
with open("intents.json") as file:
    data = json.load(file)

# Initialize variables
words, labels, docs_x, docs_y, training, output = [], [], [], [], [], []

# Process data
for intent in data["intents"]:
    for pattern in intent["patterns"]:
        tokenized_words = nltk.word_tokenize(pattern)
        words.extend(tokenized_words)
        docs_x.append(tokenized_words)
        docs_y.append(intent["tag"])

    if intent["tag"] not in labels:
        labels.append(intent["tag"])

# Stemming and removing duplicates
words = sorted(set(stemmer.stem(w.lower()) for w in words if w != "?"))
labels = sorted(labels)

# Prepare training data
out_empty = [0] * len(labels)

for x, doc in enumerate(docs_x):
    bag = [1 if stemmer.stem(w) in [stemmer.stem(w.lower()) for w in doc] else 0 for w in words]
    output_row = list(out_empty)
    output_row[labels.index(docs_y[x])] = 1
    training.append(bag)
    output.append(output_row)

# Convert to numpy arrays
training, output = np.array(training), np.array(output)


net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

# Functions for loading and training the model
def load_model():
    model.load("models/intents/model.tflearn")
    
def train_model():
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("models/intents/model.tflearn")

def bag_of_words(s):
    bag = [0] * len(words)
    s_words = [stemmer.stem(word.lower()) for word in nltk.word_tokenize(s)]
    bag = [1 if w in s_words else 0 for w in words]
    return np.array(bag)


def predict(text):
    results = model.predict([bag_of_words(text)])
    results_index = np.argmax(results)
    tag = labels[results_index]
    confidence = results[0][results_index]

    if debug:
        print(f"Results: {results}")
        print(f"Results index: {results_index}")
        print(f"Tag: {tag}")

    return tag, confidence



train_model()