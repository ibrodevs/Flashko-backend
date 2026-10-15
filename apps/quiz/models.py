from django.db import models
from django.conf import settings
from apps.flashcards.models import FlashcardSet, Flashcard


class StudySession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_sessions')
    set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='quiz_sessions')
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    mistakes_only = models.BooleanField(default=False)

    # Store prepared questions: list of {
    #   "question_id": int,
    #   "term": str,
    #   "question": str,
    #   "options": [{"id": "a", "text": "opt1"}, ...],
    #   "correct_option": "c",
    #   "correct_text": "opt3"
    # }
    questions_data = models.JSONField(default=list)
    current_question_index = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'set', 'is_completed'], name='quiz_session_active_idx'),
            models.Index(fields=['user', 'created_at'], name='quiz_session_user_date_idx'),
        ]

    def __str__(self):
        return f"Session #{self.id} - {self.set.title} ({self.user.username})"


class StudyAnswer(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name='answers')
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='study_answers')
    selected_answer = models.TextField()
    selected_option = models.CharField(max_length=10)
    correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'correct'], name='quiz_answer_result_idx'),
            models.Index(fields=['flashcard', 'correct'], name='quiz_answer_card_idx'),
        ]

    def __str__(self):
        return f"Answer in session #{self.session.id}: card {self.flashcard_id} - {'Correct' if self.correct else 'Incorrect'}"
