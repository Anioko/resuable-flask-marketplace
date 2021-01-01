import os

import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

basedir = os.path.abspath(os.path.dirname(__file__))
spam_file = basedir+'/../assets/data/spam.csv'


class SpamDetector:
    message = str

    def setMessage(self, message):
        self.message = message

    def predict(self):
        message = self.message
        df = pd.read_csv(spam_file, encoding="latin-1")
        df.drop(['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], axis=1, inplace=True)
        # Features and Labels
        df['label'] = df['class'].map({'ham': 0, 'spam': 1})
        X = df['message']
        y = df['label']

        # Extract Feature With CountVectorizer
        cv = CountVectorizer()
        X = cv.fit_transform(X)  # Fit the Data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
        # Naive Bayes Classifier
        from sklearn.naive_bayes import MultinomialNB

        clf = MultinomialNB()
        clf.fit(X_train, y_train)
        clf.score(X_test, y_test)

        data = [message]
        vect = cv.transform(data).toarray()
        my_prediction = clf.predict(vect)

        return my_prediction
