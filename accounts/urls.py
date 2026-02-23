from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('', views.feed_view, name='feed'),
    path('post/create/', views.post_create_view, name='post_create'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.comment_post, name='comment_post'),
    path('follow/request/<int:to_user_id>/', views.send_follow_request, name='send_follow_request'),
    path('follow/respond/<int:request_id>/', views.respond_follow_request, name='respond_follow_request'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/bulk-delete/', views.bulk_delete_posts, name='bulk_delete_posts'),
    path('analytics/', views.analytics_view, name='analytics'),
]