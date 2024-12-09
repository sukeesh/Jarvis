from django.test import TestCase
from django.contrib.auth.models import User
from forums.models import Post, Reply
from django.urls import reverse


class ForumsTests(TestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        # Create a post for testing
        self.post = Post.objects.create(title="Test Post", content="This is a test post.", author=self.user)

    def test_forums_home_view(self):
        response = self.client.get(reverse('forums_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forums/forums_home.html')
        self.assertContains(response, "Test Post")

    def test_post_detail_view(self):
        response = self.client.get(reverse('post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forums/post_detail.html')
        self.assertContains(response, "Test Post")

    def test_create_post(self):
        response = self.client.post(reverse('create_post'), {
            'title': 'Another Test Post',
            'content': 'Content of the new test post.',
        })
        self.assertEqual(response.status_code, 302)  # Redirects after successful post creation
        self.assertEqual(Post.objects.count(), 2)  # Ensure post is created

    def test_like_post(self):
        # Test liking a post
        response = self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # Redirects after like
        self.assertEqual(self.post.likes.count(), 1)

        # Test unliking a post
        response = self.client.post(reverse('like_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # Redirects after unlike
        self.assertEqual(self.post.likes.count(), 0)

    def test_delete_post(self):
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # Redirects after delete
        self.assertEqual(Post.objects.count(), 0)  # Ensure post is deleted

    def test_create_reply(self):
        response = self.client.post(reverse('post_detail', args=[self.post.id]), {
            'content': 'This is a test reply.',
        })
        self.assertEqual(response.status_code, 302)  # Redirects after reply creation
        self.assertEqual(Reply.objects.count(), 1)  # Ensure reply is created
        reply = Reply.objects.first()
        self.assertEqual(reply.content, 'This is a test reply.')
        self.assertEqual(reply.post, self.post)

    def test_delete_reply(self):
        reply = Reply.objects.create(content="Test Reply", post=self.post, author=self.user)
        response = self.client.post(reverse('delete_reply', args=[reply.id]))
        self.assertEqual(response.status_code, 302)  # Redirects after delete
        self.assertEqual(Reply.objects.count(), 0)  # Ensure reply is deleted

    def test_my_posts_view(self):
        response = self.client.get(reverse('my_posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forums/my_posts.html')
        self.assertContains(response, "Test Post")

    def test_my_replies_view(self):
        reply = Reply.objects.create(content="Test Reply", post=self.post, author=self.user)
        response = self.client.get(reverse('my_replies'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forums/my_replies.html')
        self.assertContains(response, "Test Reply")

    def test_my_likes_view(self):
        self.post.likes.add(self.user)
        response = self.client.get(reverse('my_likes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forums/my_likes.html')
        self.assertContains(response, "Test Post")
