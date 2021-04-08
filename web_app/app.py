import os
import warnings
import nexmo
from flask import Flask, json, render_template, url_for, request, session
import pickle
import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

myapp = Flask(__name__)

@myapp.route('/predict', methods=['POST'])
def predict():
    model = pickle.load(open("../model/spam_model.pkl", "rb"))
    tfidf_model = pickle.load(open("../model/tfidf_model.pkl", "rb"))
    if request.method == "POST":
        bool_is_json = request.is_json
        if not bool_is_json:
            return json.jsonify("{\"result\": \"invalid JSON format\"}"), 400
        else:
            id = request.json.get("id", None)
            number = request.json.get("number", None)
            message = request.json.get("message_body", None)
            print("request components : ")
            print("id : ", id)           
            print("number : ", number)
            print("message: ", message)
            spam = False #set by DMM 

            message = message.str.replace(
            r'^.+@[^\.].*\.[a-z]{2,}$', 'emailaddress')
            message = message.str.replace(
                r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$', 'webaddress')
            message = message.str.replace(r'£|\$', 'money-symbol')
            message = message.str.replace(
                r'^\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$', 'phone-number')
            message = message.str.replace(r'\d+(\.\d+)?', 'number')
            message = message.str.replace(r'[^\w\d\s]', ' ')
            message = message.str.replace(r'\s+', ' ')
            message = message.str.replace(r'^\s+|\s*?$', ' ')
            message = message.str.lower()

            stop_words = set(stopwords.words('english'))
            message = message.apply(lambda x: ' '.join(
                term for term in x.split() if term not in stop_words))
            ss = nltk.SnowballStemmer("english")
            message = message.apply(lambda x: ' '.join(ss.stem(term)
                                                                    for term in x.split()))

            # tfidf_model = TfidfVectorizer()
            tfidf_vec = tfidf_model.transform(message)
            tfidf_data = pd.DataFrame(tfidf_vec.toarray())
            my_prediction = model.predict(tfidf_data)

            spam = my_prediction

            # str = {"result" : "This be a valid req niqqa", "id": "" + id + ""}
            result = {"result" : "This be a valid req niqqa", "id": "" + id + "", "spam" : "" + str(spam) + ""}
            return json.dumps(result)
    else:
            return json.jsonify("{\"result\": \"API only responds to POST request\"}"), 400

if __name__ == '__main__':
    myapp.run(port=5000, debug=True)