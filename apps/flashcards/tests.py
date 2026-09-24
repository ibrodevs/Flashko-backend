from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import FlashcardSet, Flashcard

User = get_user_model()

class FlashcardsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', email='u1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='u2@example.com', password='pass')
        self.client.force_authenticate(user=self.user1)

    def test_create_set_with_cards(self):
        data = {
            'title': 'Bash Commands',
            'description': 'Essential terminal commands',
            'cards': [
                {'term': 'pwd', 'definition': 'print working directory'},
                {'term': 'ls', 'definition': 'list directory contents'},
                {'term': 'cd', 'definition': 'change directory'},
                {'term': 'mkdir', 'definition': 'make directory'}
            ]
        }
        response = self.client.post('/api/sets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Bash Commands')
        self.assertEqual(len(response.data['cards']), 4)
        self.assertEqual(response.data['cards_count'], 4)

    def test_user_cannot_access_others_set(self):
        other_set = FlashcardSet.objects.create(user=self.user2, title='Private Set')
        response = self.client.get(f'/api/sets/{other_set.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_set(self):
        my_set = FlashcardSet.objects.create(user=self.user1, title='To Delete')
        Flashcard.objects.create(set=my_set, term='t', definition='d')
        response = self.client.delete(f'/api/sets/{my_set.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FlashcardSet.objects.filter(id=my_set.id).exists())
        self.assertFalse(Flashcard.objects.filter(term='t').exists())
