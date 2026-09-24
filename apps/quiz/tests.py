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

    def test_quiz_draft_and_resume(self):
        # 1. Start quiz
        start_res = self.client.post('/api/quiz/start/', {'set_id': self.flashcard_set.id}, format='json')
        session_id = start_res.data['session_id']
        
        # 2. Answer first question
        q = start_res.data['question']
        self.client.post(f'/api/quiz/{session_id}/answer/', {
            'question_id': q['question_id'],
            'selected_option': q['options'][0]['id']
        }, format='json')

        # 3. Check set detail includes active_session
        set_res = self.client.get(f'/api/sets/{self.flashcard_set.id}/')
        self.assertEqual(set_res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(set_res.data['active_session'])
        self.assertEqual(set_res.data['active_session']['session_id'], session_id)
        self.assertEqual(set_res.data['active_session']['current_question_index'], 1)

        # 4. Resume quiz via GET /api/quiz/{session_id}/
        resume_res = self.client.get(f'/api/quiz/{session_id}/')
        self.assertEqual(resume_res.status_code, status.HTTP_200_OK)
        self.assertEqual(resume_res.data['current_question']['question_number'], 2)

        # 5. Discard draft session
        discard_res = self.client.post(f'/api/quiz/{session_id}/discard/')
        self.assertEqual(discard_res.status_code, status.HTTP_200_OK)
        
        # After discard, active_session is None
        set_res_after = self.client.get(f'/api/sets/{self.flashcard_set.id}/')
        self.assertIsNone(set_res_after.data['active_session'])

    def test_review_all_mistakes(self):
        # Start and intentionally fail question
        start_res = self.client.post('/api/quiz/start/', {'set_id': self.flashcard_set.id}, format='json')
        session_id = start_res.data['session_id']
        q = start_res.data['question']
        
        # Answer with a wrong option or simulate incorrect answer
        ans_res = self.client.post(f'/api/quiz/{session_id}/answer/', {
            'question_id': q['question_id'],
            'selected_option': 'a'
        }, format='json')
        
        # If it happened to be correct, pick a wrong one for the second question
        if ans_res.data['correct']:
            q2 = ans_res.data['next_question']
            wrong_opt = 'b' if ans_res.data['correct_option'] != 'b' else 'c'
            ans_res = self.client.post(f'/api/quiz/{session_id}/answer/', {
                'question_id': q2['question_id'],
                'selected_option': wrong_opt
            }, format='json')

        # Now test review mistakes without from_session_id
        mistake_quiz = self.client.post('/api/quiz/start/', {
            'set_id': self.flashcard_set.id,
            'mistakes_only': True
        }, format='json')
        self.assertEqual(mistake_quiz.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mistake_quiz.data['total_questions'] >= 1)

