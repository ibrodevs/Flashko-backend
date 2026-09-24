from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.flashcards.models import FlashcardSet, Flashcard
from .models import StudySession

User = get_user_model()

class QuizAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='quizuser', email='q@example.com', password='pass')
        self.client.force_authenticate(user=self.user)
        
        self.flashcard_set = FlashcardSet.objects.create(user=self.user, title='Test Set')
        self.cards = [
            Flashcard.objects.create(set=self.flashcard_set, term='sudo', definition='super user do'),
            Flashcard.objects.create(set=self.flashcard_set, term='pwd', definition='print working directory'),
            Flashcard.objects.create(set=self.flashcard_set, term='ls', definition='list files'),
            Flashcard.objects.create(set=self.flashcard_set, term='rm', definition='remove files')
        ]

    def test_quiz_requires_minimum_4_cards(self):
        small_set = FlashcardSet.objects.create(user=self.user, title='Small Set')
        Flashcard.objects.create(set=small_set, term='a', definition='b')
        response = self.client.post('/api/quiz/start/', {'set_id': small_set.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('минимум 4', response.data['detail'])

    def test_quiz_flow(self):
        # 1. Start quiz
        start_res = self.client.post('/api/quiz/start/', {'set_id': self.flashcard_set.id}, format='json')
        self.assertEqual(start_res.status_code, status.HTTP_201_CREATED)
        session_id = start_res.data['session_id']
        self.assertEqual(start_res.data['total_questions'], 4)
        
        q = start_res.data['question']
        self.assertIn('question_id', q)
        self.assertEqual(len(q['options']), 4)
        # Verify correct_option is not leaked in question
        self.assertNotIn('correct_option', q)

        # 2. Answer question
        # Pick first option
        opt_id = q['options'][0]['id']
        ans_res = self.client.post(f'/api/quiz/{session_id}/answer/', {
            'question_id': q['question_id'],
            'selected_option': opt_id
        }, format='json')
        
        self.assertEqual(ans_res.status_code, status.HTTP_200_OK)
        self.assertIn('correct', ans_res.data)
        self.assertIn('correct_option', ans_res.data)
        self.assertEqual(ans_res.data['total_questions'], 4)
        self.assertEqual(ans_res.data['current_question_index'], 1)
