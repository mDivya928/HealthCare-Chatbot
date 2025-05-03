#!/usr/bin/env python3
import json
import re
import pickle
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier

# Download required NLTK data (only the first time)
nltk.download('punkt', quiet=True)

def clean_text(text: str) -> str:
    text = text.lower()
    return re.sub(r'[^a-z0-9\\s]', '', text)

def main():
    # 1) Load intents
    with open('data/intents.json', 'r') as f:
        data = json.load(f)

    sentences, labels = [], []
    for intent in data['intents']:
        for pattern in intent['patterns']:
            sentences.append(clean_text(pattern))
            labels.append(intent['tag'])

    # 2) Vectorize
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)

    # 3) Encode labels
    le = LabelEncoder()
    y = le.fit_transform(labels)

    # 4) Train classifier
    model = MLPClassifier(hidden_layer_sizes=(8, 8), max_iter=500)
    model.fit(X, y)

    # 5) Persist artifacts
    import os
    os.makedirs('models', exist_ok=True)
    with open('models/vectorizer.pkl',    'wb') as f: pickle.dump(vectorizer, f)
    with open('models/label_encoder.pkl', 'wb') as f: pickle.dump(le, f)
    with open('models/intent_model.pkl',   'wb') as f: pickle.dump(model, f)

    print('✅ Model training complete — artifacts saved into models/')

if __name__ == '__main__':
    main()
