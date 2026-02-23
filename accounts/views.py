from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from textblob import TextBlob

from .models import CustomUser, Post, Like, Comment, FollowRequest
from .forms import RegisterForm, PostForm


# ================= REGISTER =================
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'social/register.html', {'form': form})


# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('feed')
    return render(request, 'social/login.html')


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect('login')


# ================= PROFILE =================
@login_required
def profile_view(request):
    user = request.user
    followers_count = user.followers.count()
    following_count = user.following.count()
    posts_count = Post.objects.filter(author=user).count()

    return render(request, 'social/profile.html', {
        'followers_count': followers_count,
        'following_count': following_count,
        'posts_count': posts_count
    })


# ================= FEED =================
@login_required
def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')

    for post in posts:
        followers = post.author.followers.count()
        likes = post.like_set.count()
        comments = post.comment_set.count()

        if followers > 0:
            post.engagement_score = round((likes + comments * 2) / followers, 2)
        else:
            post.engagement_score = 0

    follow_requests = FollowRequest.objects.filter(
        to_user=request.user,
        status='pending'
    )

    return render(request, 'social/feed.html', {
        'posts': posts,
        'follow_requests': follow_requests
    })


# ================= CREATE POST WITH SENTIMENT =================
from .dl_model import train_model, predict_likes
from textblob import TextBlob
from django.contrib.auth.decorators import login_required

@login_required
def post_create_view(request):

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():

            caption = form.cleaned_data['caption']
            image = form.cleaned_data.get('image')

            suggestions = []

            # 🔹 SENTIMENT ANALYSIS
            blob = TextBlob(caption)
            sentiment_score = blob.sentiment.polarity

            if sentiment_score > 0.3:
                sentiment_label = "Positive 😊"
                suggestions.append("Great! Your caption has a positive tone.")
            elif sentiment_score < -0.3:
                sentiment_label = "Negative 😔"
                suggestions.append("Your caption feels negative. Try improving tone.")
            else:
                sentiment_label = "Neutral 😐"
                suggestions.append("Neutral caption detected. Add emotion for better engagement.")

            # 🔹 Caption checks
            if len(caption) < 20:
                suggestions.append("Caption is too short. Longer captions perform better.")

            if "#" not in caption:
                suggestions.append("Add hashtags to improve reach.")

            if not image:
                suggestions.append("Posts with images get more engagement.")

            # 🔥 DEEP LEARNING PREDICTION
            all_posts = Post.objects.all()
            model = train_model(all_posts)

            followers = request.user.followers.count()
            caption_length = len(caption)
            has_image = 1 if image else 0

            prediction = predict_likes(
                model,
                followers,
                caption_length,
                has_image
            )

            # Safety limits
            if prediction < 0:
                prediction = 0

            if prediction > followers:
                prediction = followers

            # 🔥 Better Engagement Logic

            if followers == 0:
                engagement_level = "Low ❄"

            elif prediction == 0:
                 engagement_level = "Needs Improvement 📉"

            else:
                 ratio = prediction / followers

                 if ratio >= 0.6:
                         engagement_level = "High 🔥"
                 elif ratio >= 0.3:
                         engagement_level = "Medium ⚡"
                 else:
                         engagement_level = "Low ❄"

            # Save Post
            post = form.save(commit=False)
            post.author = request.user
            post.predicted_likes = prediction
            post.sentiment = sentiment_label
            post.engagement_level = engagement_level
            post.save()

            return render(request, 'social/prediction.html', {
                'predicted_likes': prediction,
                'sentiment': sentiment_label,
                'suggestions': suggestions,
                'engagement_level': engagement_level
            })

    else:
        form = PostForm()

    return render(request, 'social/post_form.html', {'form': form})

# ================= LIKE =================
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        like.delete()
        messages.success(request, "💔 You unliked the post.")
    else:
        messages.success(request, "❤️ You liked the post.")

    return redirect('feed')


# ================= COMMENT =================
@login_required
def comment_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )

    return redirect('feed')


# ================= FOLLOW =================
@login_required
@require_POST
def send_follow_request(request, to_user_id):
    to_user = get_object_or_404(CustomUser, id=to_user_id)

    if request.user != to_user:
        FollowRequest.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            status='pending'
        )

    return redirect('feed')


@login_required
@require_POST
def respond_follow_request(request, request_id):
    follow_request = get_object_or_404(
        FollowRequest,
        id=request_id,
        to_user=request.user
    )

    action = request.POST.get('action')

    if action == 'accept':
        follow_request.status = 'accepted'
        follow_request.to_user.followers.add(follow_request.from_user)
    elif action == 'reject':
        follow_request.status = 'rejected'

    follow_request.save()
    return redirect('feed')


# ================= DELETE POST =================
@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, "Post deleted successfully 🗑️")
    return redirect('feed')


# ================= BULK DELETE =================
@login_required
@require_POST
def bulk_delete_posts(request):
    selected_ids = request.POST.getlist('selected_posts')

    Post.objects.filter(
        id__in=selected_ids,
        author=request.user
    ).delete()

    messages.success(request, "Selected posts deleted successfully 🗑️")
    return redirect('feed')

from django.db.models import Avg, Count
import matplotlib.pyplot as plt
import io
import base64

@login_required
def analytics_view(request):

    posts = Post.objects.all()

    total_posts = posts.count()

    avg_likes = posts.aggregate(Avg('predicted_likes'))['predicted_likes__avg']
    if avg_likes is None:
        avg_likes = 0

    # Sentiment count
    positive = posts.filter(sentiment__icontains="Positive").count()
    neutral = posts.filter(sentiment__icontains="Neutral").count()
    negative = posts.filter(sentiment__icontains="Negative").count()

    # Most engaging post
    top_post = posts.order_by('-predicted_likes').first()

    # 🔥 Create Bar Chart
    captions = [p.caption[:10] + "..." for p in posts]
    likes = [p.predicted_likes for p in posts]

    plt.figure()
    plt.bar(captions, likes)
    plt.xticks(rotation=45)

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    image_png = buffer.getvalue()
    buffer.close()

    chart = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'social/analytics.html', {
        'total_posts': total_posts,
        'avg_likes': round(avg_likes, 2),
        'positive': positive,
        'neutral': neutral,
        'negative': negative,
        'top_post': top_post,
        'chart': chart
    })