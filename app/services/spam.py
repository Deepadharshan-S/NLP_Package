import pickle
import os
import nltk
from nltk.corpus import stopwords 
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../model/spam_models.pkl")

with open(MODEL_PATH, "rb") as f:
    models = pickle.load(f)

tfid = models["tfidf"]
rfc = models["rfc"]
mnb = models["mnb"]
bc = models["bc"]
etc = models["etc"]
lrc = models["lrc"]


nltk.download('stopwords')   # Downloading stopwords data
nltk.download('punkt')       # Downloading tokenizer data
nltk.download('punkt_tab')

from nltk.stem.porter import PorterStemmer

import string

ps = PorterStemmer()

def transform_text(text):
    text = text.lower()
    
    text = nltk.word_tokenize(text)
    
    y = []
    for i in text:
        if i.isalnum():
            y.append(i)
            
    text = y[:]
    y.clear()
    
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
        
    text = y[:]
    y.clear()
    for i in text:
        y.append(ps.stem(i))
    
    # Join the processed tokens back into a single string
    return " ".join(y)

def predict_spam(text: str):
    transformed = transform_text(text)
    vector_input = tfid.transform([transformed])

    preds = [
        rfc.predict(vector_input)[0],
        mnb.predict(vector_input)[0],
        bc.predict(vector_input)[0],
        etc.predict(vector_input)[0],
        lrc.predict(vector_input)[0]
    ]

    is_spam = sum(preds) >= 2
    confidence = sum(preds) / len(preds)

    return bool(is_spam), float(confidence)