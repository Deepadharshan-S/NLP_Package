def predict_spam(text: str):
    spam_keywords = ["win", "free", "money", "offer", "click"]

    text = text.lower()

    for word in spam_keywords:
        if word in text:
            return True, 0.9

    return False, 0.1