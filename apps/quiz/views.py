import random
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.flashcards.models import FlashcardSet, Flashcard
from .models import StudySession, StudyAnswer
from .serializers import StudySessionSerializer, QuizStartSerializer, QuizAnswerSerializer

class QuizStartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QuizStartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        set_id = serializer.validated_data['set_id']
        mistakes_only = serializer.validated_data.get('mistakes_only', False)
        from_session_id = serializer.validated_data.get('from_session_id')

        flashcard_set = get_object_or_404(FlashcardSet, pk=set_id, user=request.user)
        all_cards = list(flashcard_set.cards.all())

        if len(all_cards) < 4:
            return Response({
                'detail': 'Для запуска теста требуется минимум 4 карточки.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Decide which cards to test
        if mistakes_only:
            target_cards = []
            if from_session_id:
                prev_session = get_object_or_404(StudySession, pk=from_session_id, user=request.user)
                mistake_ids = prev_session.answers.filter(correct=False).values_list('flashcard_id', flat=True).distinct()
                target_cards = [c for c in all_cards if c.id in mistake_ids]
            else:
                mistake_ids = StudyAnswer.objects.filter(
                    session__set=flashcard_set,
                    session__user=request.user,
                    correct=False
                ).values_list('flashcard_id', flat=True).distinct()
                target_cards = [c for c in all_cards if c.id in mistake_ids]
            
            if not target_cards:
                # If no session specified or no mistakes found
                return Response({
                    'detail': 'Нет карточек с ошибками для повторения.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_cards = list(all_cards)

        # Shuffle questions
        random.shuffle(target_cards)

        questions_data = []
        option_letters = ['a', 'b', 'c', 'd']

        for card in target_cards:
            correct_def = card.definition.strip()
            # Distractors from other cards
            other_defs = list({c.definition.strip() for c in all_cards if c.id != card.id and c.definition.strip() != correct_def})
            
            # If not enough distinct definitions, fall back to other cards' definitions anyway
            if len(other_defs) < 3:
                other_defs = [c.definition.strip() for c in all_cards if c.id != card.id]
            
            # Sample 3 distractors
            if len(other_defs) >= 3:
                distractors = random.sample(other_defs, 3)
            else:
                distractors = (other_defs * 3)[:3]

            choices = [correct_def] + distractors
            random.shuffle(choices)

            options = []
            correct_option = None
            for idx, choice_text in enumerate(choices):
                letter = option_letters[idx]
                options.append({
                    'id': letter,
                    'text': choice_text
                })
                if choice_text == correct_def and correct_option is None:
                    correct_option = letter

            questions_data.append({
                'question_id': card.id,
                'term': card.term,
                'question': f'Что означает «{card.term}»?',
                'options': options,
                'correct_option': correct_option,
                'correct_text': correct_def
            })

        # Archive any previous uncompleted sessions for this set so user only has 1 active draft
        StudySession.objects.filter(
            user=request.user,
            set=flashcard_set,
            is_completed=False
        ).update(is_completed=True, completed_at=timezone.now())

        session = StudySession.objects.create(
            user=request.user,
            set=flashcard_set,
            total_questions=len(questions_data),
            correct_answers=0,
            incorrect_answers=0,
            is_completed=False,
            mistakes_only=mistakes_only,
            questions_data=questions_data,
            current_question_index=0
        )


        first_q = questions_data[0]
        # Never send correct_option or correct_text in options payload
        client_question = {
            'question_id': first_q['question_id'],
            'term': first_q['term'],
            'question': first_q['question'],
            'options': first_q['options'],
            'question_number': 1,
            'total_questions': len(questions_data)
        }

        return Response({
            'session_id': session.id,
            'set_id': flashcard_set.id,
            'set_title': flashcard_set.title,
            'total_questions': len(questions_data),
            'current_question_index': 0,
            'mistakes_only': mistakes_only,
            'question': client_question
        }, status=status.HTTP_201_CREATED)

class QuizAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(StudySession, pk=session_id, user=request.user)

        if session.is_completed:
            return Response({
                'detail': 'Тестирование уже завершено.',
                'is_completed': True,
                'correct_count': session.correct_answers,
                'incorrect_count': session.incorrect_answers,
                'total_questions': session.total_questions,
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuizAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question_id = serializer.validated_data['question_id']
        selected_option = serializer.validated_data['selected_option'].lower().strip()

        curr_idx = session.current_question_index
        if curr_idx >= len(session.questions_data):
            session.is_completed = True
            session.completed_at = timezone.now()
            session.save()
            return Response({'detail': 'Все вопросы пройдены.', 'is_completed': True}, status=status.HTTP_200_OK)

        q_data = session.questions_data[curr_idx]
        if q_data['question_id'] != question_id:
            return Response({'detail': 'Идентификатор вопроса не совпадает с текущим.'}, status=status.HTTP_400_BAD_REQUEST)

        is_correct = (selected_option == q_data['correct_option'])
        
        # Find selected text
        selected_text = ''
        for opt in q_data['options']:
            if opt['id'] == selected_option:
                selected_text = opt['text']
                break

        # Save StudyAnswer
        card = get_object_or_404(Flashcard, pk=question_id)
        StudyAnswer.objects.create(
            session=session,
            flashcard=card,
            selected_answer=selected_text or selected_option,
            selected_option=selected_option,
            correct=is_correct
        )

        if is_correct:
            session.correct_answers += 1
        else:
            session.incorrect_answers += 1

        session.current_question_index += 1
        if session.current_question_index >= session.total_questions:
            session.is_completed = True
            session.completed_at = timezone.now()

        session.save()

        next_question = None
        if not session.is_completed and session.current_question_index < len(session.questions_data):
            next_q_data = session.questions_data[session.current_question_index]
            next_question = {
                'question_id': next_q_data['question_id'],
                'term': next_q_data['term'],
                'question': next_q_data['question'],
                'options': next_q_data['options'],
                'question_number': session.current_question_index + 1,
                'total_questions': session.total_questions
            }

        return Response({
            'correct': is_correct,
            'correct_option': q_data['correct_option'],
            'correct_text': q_data['correct_text'],
            'selected_option': selected_option,
            'correct_count': session.correct_answers,
            'incorrect_count': session.incorrect_answers,
            'total_questions': session.total_questions,
            'current_question_index': session.current_question_index,
            'is_completed': session.is_completed,
            'next_question': next_question
        }, status=status.HTTP_200_OK)

class QuizDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(StudySession, pk=session_id, user=request.user)
        serializer = StudySessionSerializer(session)
        data = dict(serializer.data)
        data['session_id'] = session.id
        data['set_id'] = session.set.id
        data['set_title'] = session.set.title
        data['correct_count'] = session.correct_answers
        data['incorrect_count'] = session.incorrect_answers
        
        # If not completed, include current question
        if not session.is_completed and session.current_question_index < len(session.questions_data):
            curr_q = session.questions_data[session.current_question_index]
            client_q = {
                'question_id': curr_q['question_id'],
                'term': curr_q['term'],
                'question': curr_q['question'],
                'options': curr_q['options'],
                'question_number': session.current_question_index + 1,
                'total_questions': session.total_questions
            }
            data['current_question'] = client_q
            data['question'] = client_q
        return Response(data, status=status.HTTP_200_OK)

class QuizDiscardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(StudySession, pk=session_id, user=request.user)
        if not session.is_completed:
            session.is_completed = True
            session.completed_at = timezone.now()
            session.save()
        return Response({'detail': 'Черновик теста отменен.'}, status=status.HTTP_200_OK)

class QuizFinishView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(StudySession, pk=session_id, user=request.user)
        if not session.is_completed:
            session.is_completed = True
            session.completed_at = timezone.now()
            session.save()
        serializer = StudySessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)

