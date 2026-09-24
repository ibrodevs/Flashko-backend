from rest_framework import serializers
from .models import StudySession, StudyAnswer
from apps.flashcards.serializers import FlashcardSerializer

class StudyAnswerSerializer(serializers.ModelSerializer):
    flashcard = FlashcardSerializer(read_only=True)

    class Meta:
        model = StudyAnswer
        fields = ['id', 'flashcard', 'selected_answer', 'selected_option', 'correct', 'created_at']

class StudySessionSerializer(serializers.ModelSerializer):
    set_title = serializers.CharField(source='set.title', read_only=True)
    answers = StudyAnswerSerializer(many=True, read_only=True)
    mistake_card_ids = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = StudySession
        fields = [
            'id', 'set', 'set_title', 'total_questions', 'correct_answers',
            'incorrect_answers', 'percentage', 'is_completed', 'mistakes_only',
            'current_question_index', 'created_at', 'completed_at', 'mistake_card_ids', 'answers'
        ]

    def get_percentage(self, obj):
        if obj.total_questions == 0:
            return 0
        return round((obj.correct_answers / obj.total_questions) * 100)

    def get_mistake_card_ids(self, obj):
        return list(obj.answers.filter(correct=False).values_list('flashcard_id', flat=True).distinct())

class QuizStartSerializer(serializers.Serializer):
    set_id = serializers.IntegerField(required=True)
    mistakes_only = serializers.BooleanField(required=False, default=False)
    from_session_id = serializers.IntegerField(required=False, allow_null=True)

class QuizAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=True)
    selected_option = serializers.CharField(required=True, max_length=10)
