from django.contrib import admin
from django.db.models import Count
from .models import CustomUser, Profile, Post, Like, Comment, FollowRequest


# ================= USERS =================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')
    search_fields = ('username', 'email')


# ================= PROFILE =================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')


# ================= POSTS =================
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'caption', 'created_at')
    list_filter = ('created_at',)


# ================= LIKES =================
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')


# ================= COMMENTS =================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')


# ================= FOLLOW REQUESTS =================
@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status')
