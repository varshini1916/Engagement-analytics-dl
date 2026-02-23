from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ================= CUSTOM USER =================
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="following",
        blank=True
    )

    def __str__(self):
        return self.username


# ================= PROFILE =================
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.jpg'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ================= POST =================
class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='posts/images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    predicted_likes = models.IntegerField(default=0)
    sentiment = models.CharField(max_length=20, blank=True)   

    def total_likes(self):
        return self.like_set.count()

    def __str__(self):
        return f"{self.author.username} - {self.caption[:30]}"


# ================= LIKE =================
class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


# ================= COMMENT =================
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ================= FOLLOW REQUEST =================
class FollowRequest(models.Model):
    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_requests'
    )
    to_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_requests'
    )

    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    status = models.CharField(
        max_length=10,
        choices=status_choices,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"
