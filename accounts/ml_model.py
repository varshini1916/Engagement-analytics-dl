import numpy as np
from sklearn.linear_model import LinearRegression
from .models import Post, Like

def extract_features(posts):
    X = []
    y = []

    for post in posts:
        caption_length = len(post.caption)
        has_image = 1 if post.image else 0
        likes_count = Like.objects.filter(post=post).count()

        X.append([caption_length, has_image])
        y.append(likes_count)

    return np.array(X), np.array(y)

def train_model():
    posts = Post.objects.all()

    if posts.count() < 2:
        return None  # not enough data

    X, y = extract_features(posts)

    model = LinearRegression()
    model.fit(X, y)

    return model

def predict_likes(model, caption, has_image):
    if model is None:
        return 0

    features = np.array([[len(caption), has_image]])
    prediction = model.predict(features)

    return max(0, int(prediction[0]))
