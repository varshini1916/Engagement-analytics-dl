import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def train_model(posts):

    X = []
    y = []

    for post in posts:
        followers = post.author.followers.count()
        caption_length = len(post.caption)
        has_image = 1 if post.image else 0
        likes = post.like_set.count()

        X.append([followers, caption_length, has_image])
        y.append(likes)

    if len(X) < 2:
        return None

    X = np.array(X)
    y = np.array(y)

    model = keras.Sequential([
        layers.Dense(8, activation='relu', input_shape=(3,)),
        layers.Dense(4, activation='relu'),
        layers.Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')

    model.fit(X, y, epochs=50, verbose=0)

    return model


def predict_likes(model, followers, caption_length, has_image):

    if model is None:
        return 0

    input_data = np.array([[followers, caption_length, has_image]])
    prediction = model.predict(input_data, verbose=0)

    return max(0, int(prediction[0][0]))