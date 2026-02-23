import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

MAX_WORDS = 5000
MAX_LEN = 50

tokenizer = Tokenizer(num_words=MAX_WORDS)

def train_dl_model(posts):
    captions = []
    likes = []

    for post in posts:
        if post.caption:
            captions.append(post.caption)
            likes.append(post.total_likes())

    if len(captions) < 5:
        return None

    tokenizer.fit_on_texts(captions)
    sequences = tokenizer.texts_to_sequences(captions)
    X = pad_sequences(sequences, maxlen=MAX_LEN)
    y = np.array(likes)

    model = Sequential()
    model.add(Embedding(MAX_WORDS, 64, input_length=MAX_LEN))
    model.add(LSTM(32))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(1))

    model.compile(loss='mse', optimizer='adam')
    model.fit(X, y, epochs=8, verbose=0)

    return model


def predict_dl(user, caption, has_image):

    # If no caption and no image → no prediction
    if not caption and not has_image:
        return 0

    followers = user.followers.count()

    user_posts = user.post_set.all()
    total_likes = sum([p.like_set.count() for p in user_posts])
    avg_likes = total_likes / user_posts.count() if user_posts.exists() else 0

    from textblob import TextBlob
    polarity = TextBlob(caption).sentiment.polarity if caption else 0

    if polarity > 0:
        sentiment_bonus = 2
    elif polarity < 0:
        sentiment_bonus = -1
    else:
        sentiment_bonus = 0

    image_bonus = 3 if has_image else 0

    prediction = int(followers + avg_likes + sentiment_bonus + image_bonus)

    if prediction < 0:
        prediction = 0

    return prediction