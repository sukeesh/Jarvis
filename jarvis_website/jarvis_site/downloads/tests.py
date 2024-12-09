from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages

class DownloadsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.login_url = reverse('login')
        self.create_account_url = reverse('create_account')
        self.account_url = reverse('account')
        self.update_email_url = reverse('update_email')
        self.change_password_url = reverse('change_password')
        self.delete_account_url = reverse('delete_account')

    def test_create_account_successful(self):
        response = self.client.post(self.create_account_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'email_confirm': 'newuser@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123',
        })
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_create_account_passwords_do_not_match(self):
        response = self.client.post(self.create_account_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'email_confirm': 'newuser@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'WrongPass123',
        })
        self.assertContains(response, "Passwords do not match.")

    def test_create_account_emails_do_not_match(self):
        response = self.client.post(self.create_account_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'email_confirm': 'wronguser@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123',
        })
        self.assertContains(response, "Emails do not match.")

    def test_login_redirect_to_account_page(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, testuser")

    def test_update_email_success(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.update_email_url, {
            'email': 'updatedemail@example.com',
            'email_confirm': 'updatedemail@example.com',
        })
        self.assertRedirects(response, self.account_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updatedemail@example.com')

    def test_update_email_failure_due_to_mismatch(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.update_email_url, {
            'email': 'updatedemail@example.com',
            'email_confirm': 'wrongemail@example.com',
        })
        self.assertContains(response, "Emails do not match.")

    def test_change_password_success(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.change_password_url, {
            'old_password': 'password123',
            'new_password1': 'NewSecurePass123',
            'new_password2': 'NewSecurePass123',
        })
        self.assertRedirects(response, self.account_url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass123'))

    def test_delete_account_success(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.delete_account_url, {
            'password': 'password123',
        })
        self.assertRedirects(response, '/')
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_delete_account_failure_due_to_wrong_password(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.delete_account_url, {
            'password': 'wrongpassword',
        })
        self.assertContains(response, "Incorrect password.")
