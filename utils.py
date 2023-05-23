import pandas as pd
import numpy as np
import re
import nltk
import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def load_data(file_path):
    # Load the data from the CSV file
    data = pd.read_csv(file_path)

    # Extract the text and labels
    text = data['text'].values
    labels = data['label'].values

    return text, labels

def preprocess_data(text, labels, max_len):
    # Remove special characters and digits
    text = [re.sub(r'\W+', ' ', str(doc)) for doc in text]
    text = [re.sub(r'\d+', '', str(doc)) for doc in text]

    # Convert to lowercase
    text = [doc.lower() for doc in text]

    # Tokenize the text
    text = [nltk.word_tokenize(doc) for doc in text]

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    text = [[word for word in doc if not word in stop_words] for doc in text]

    # Lemmatize the text
    lemmatizer = WordNetLemmatizer()
    text = [[lemmatizer.lemmatize(word) for word in doc] for doc in text]

    # Pad the sequences
    text = [doc[:max_len] + [''] * (max_len - len(doc)) for doc in text]

    # Convert the labels to one-hot encoding
    labels = np.eye(len(set(labels)))[labels]

    return np.array(text), labels

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Remove numbers
    text = re.sub(r"\d+", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove stopwords
    stopwords = ["the", "and", "a", "an", "in", "to", "of", "for", "with", "on", "at", "by", "from", "up", "about", "than", "into", "over", "after", "before", "under", "between", "out", "through", "during", "since", "without", "per", "via"]
    text_tokens = text.split()
    text_tokens = [token for token in text_tokens if token not in stopwords]
    text = " ".join(text_tokens)

    return text