from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AccountsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.me_url = '/api/auth/me/'
        self.refresh_url = '/api/auth/refresh/'
        self.logout_url = '/api/auth/logout/'

    def test_register_success(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertIn('refresh_token', response.cookies)

    def test_register_passwords_do_not_match(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different_password'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_login_by_username_and_email(self):
        User.objects.create_user(username='user1', email='user1@example.com', password='secretpassword')
        
        # Test username
        res1 = self.client.post(self.login_url, {'username_or_email': 'user1', 'password': 'secretpassword'}, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertIn('access', res1.data)
        
        # Test email
        res2 = self.client.post(self.login_url, {'username_or_email': 'user1@example.com', 'password': 'secretpassword'}, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIn('access', res2.data)

    def test_me_authenticated(self):
        user = User.objects.create_user(username='user1', email='user1@example.com', password='secretpassword')
        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')

    def test_change_password_success(self):
        user = User.objects.create_user(username='pwuser', email='pw@example.com', password='oldpassword123')
        self.client.force_authenticate(user=user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # Verify user can log in with new password
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword456'))
        self.assertFalse(user.check_password('oldpassword123'))

    def test_change_password_wrong_current(self):
        user = User.objects.create_user(username='pwuser2', email='pw2@example.com', password='oldpassword123')
        self.client.force_authenticate(user=user)
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword456',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_change_password_same_password(self):
        user = User.objects.create_user(username='pwuser3', email='pw3@example.com', password='oldpassword123')
        self.client.force_authenticate(user=user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'oldpassword123',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)

    def test_change_password_confirm_mismatch(self):
        user = User.objects.create_user(username='pwuser4', email='pw4@example.com', password='oldpassword123')
        self.client.force_authenticate(user=user)
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'differentpassword',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)
