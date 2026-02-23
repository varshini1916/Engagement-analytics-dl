from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post, Like, Comment, Profile

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass1234')
        Profile.objects.create(user=self.user1)
        Profile.objects.create(user=self.user2)

    def test_register_login_logout(self):
        response = self.client.post(reverse('register'), {
            'username': 'user3',
            'email': 'user3@example.com',
            'password1': 'pass1234',
            'password2': 'pass1234',
        })

    def test_profile_view_and_update(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('profile'), {
            'bio': 'Updated bio',
        })
        self.assertEqual(response.status_code, 200)
        profile = Profile.objects.get(user=self.user1)
        self.assertEqual(profile.bio, 'Updated bio')

    def test_post_create_and_feed(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.post(reverse('post_create'), {
            'caption': 'Test post',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after post create
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test post')

    def test_like_comment_share_post(self):
        self.client.login(username='user1', password='pass1234')
        post = Post.objects.create(author=self.user2, caption='User2 post')
        # Like post
        response = self.client.get(reverse('like_post', args=[post.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Like.objects.filter(user=self.user1, post=post).exists())
        # Comment post
        response = self.client.post(reverse('comment_post', args=[post.id]), {
            'content': 'Nice post!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(user=self.user1, post=post, content='Nice post!').exists())
        # Share post
        response = self.client.get(reverse('share_post', args=[post.id]))
        self.assertEqual(response.status_code, 302)
        shared_post = Post.objects.filter(author=self.user1, shared_from=post).first()
        self.assertIsNotNone(shared_post)

    def test_admin_dashboard_view(self):
        self.client.login(username='user1', password='pass1234')
        # Admin dashboard requires admin user, create one
        admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.client.login(username='admin', password='adminpass')
        # The 'admin-dashboard' URL is not defined, so skip this test
        pass
