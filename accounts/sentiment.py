from textblob import TextBlob

def analyze_sentiment(text):
    if not text:
        return "Neutral 😐", 0

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0:
        return "Positive 😊", polarity
    elif polarity < 0:
        return "Negative 😔", polarity
    else:
        return "Neutral 😐", polarity
