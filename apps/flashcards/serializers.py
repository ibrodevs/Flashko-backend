from rest_framework import serializers
from django.db import transaction
from .models import FlashcardSet, Flashcard

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['id', 'set', 'term', 'definition', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'set', 'created_at', 'updated_at']

    def validate_term(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Term cannot be empty.")
        return value.strip()

    def validate_definition(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Definition cannot be empty.")
        return value.strip()

class FlashcardCardItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    term = serializers.CharField(required=True)
    definition = serializers.CharField(required=True)

    def validate_term(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Term cannot be empty.")
        return value.strip()

    def validate_definition(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Definition cannot be empty.")
        return value.strip()

class FlashcardSetListSerializer(serializers.ModelSerializer):
    cards_count = serializers.SerializerMethodField()
    share_id = serializers.UUIDField(read_only=True)
    has_active_session = serializers.SerializerMethodField()
    mistakes_count = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardSet
        fields = [
            'id', 'title', 'description', 'cards_count', 'share_id',
            'has_active_session', 'mistakes_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'cards_count', 'share_id', 'has_active_session',
            'mistakes_count', 'created_at', 'updated_at'
        ]

    def get_cards_count(self, obj):
        if hasattr(obj, 'cards_count'):
            return obj.cards_count
        return obj.cards.count()

    def get_has_active_session(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        from apps.quiz.models import StudySession
        return StudySession.objects.filter(set=obj, user=request.user, is_completed=False).exists()

    def get_mistakes_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return 0
        from apps.quiz.models import StudyAnswer
        return StudyAnswer.objects.filter(
            session__set=obj,
            session__user=request.user,
            correct=False
        ).values('flashcard_id').distinct().count()

class FlashcardSetDetailSerializer(serializers.ModelSerializer):
    cards = FlashcardSerializer(many=True, read_only=True)
    cards_count = serializers.SerializerMethodField()
    share_id = serializers.UUIDField(read_only=True)
    author_username = serializers.CharField(source='user.username', read_only=True)
    active_session = serializers.SerializerMethodField()
    mistakes_count = serializers.SerializerMethodField()
    mistake_card_ids = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardSet
        fields = [
            'id', 'title', 'description', 'share_id', 'is_public',
            'author_username', 'cards_count', 'cards',
            'active_session', 'mistakes_count', 'mistake_card_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'share_id', 'author_username', 'cards_count', 'cards',
            'active_session', 'mistakes_count', 'mistake_card_ids',
            'created_at', 'updated_at'
        ]

    def get_cards_count(self, obj):
        if hasattr(obj, 'cards_count'):
            return obj.cards_count
        return obj.cards.count()

    def get_active_session(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        from apps.quiz.models import StudySession
        active = StudySession.objects.filter(set=obj, user=request.user, is_completed=False).order_by('-created_at').first()
        if active:
            return {
                'session_id': active.id,
                'current_question_index': active.current_question_index,
                'total_questions': active.total_questions,
                'correct_answers': active.correct_answers,
                'incorrect_answers': active.incorrect_answers,
                'mistakes_only': active.mistakes_only,
                'created_at': active.created_at,
            }
        return None

    def get_mistakes_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return 0
        from apps.quiz.models import StudyAnswer
        return StudyAnswer.objects.filter(
            session__set=obj,
            session__user=request.user,
            correct=False
        ).values('flashcard_id').distinct().count()

    def get_mistake_card_ids(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return []
        from apps.quiz.models import StudyAnswer
        return list(StudyAnswer.objects.filter(
            session__set=obj,
            session__user=request.user,
            correct=False
        ).values_list('flashcard_id', flat=True).distinct())


class FlashcardSetCreateUpdateSerializer(serializers.ModelSerializer):
    cards = FlashcardCardItemSerializer(many=True, required=False)

    class Meta:
        model = FlashcardSet
        fields = ['id', 'title', 'description', 'cards', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        cards_data = validated_data.pop('cards', [])
        user = self.context['request'].user
        
        with transaction.atomic():
            flashcard_set = FlashcardSet.objects.create(user=user, **validated_data)
            cards_to_create = [
                Flashcard(
                    set=flashcard_set,
                    term=card_item['term'],
                    definition=card_item['definition'],
                    order=idx
                )
                for idx, card_item in enumerate(cards_data)
            ]
            if cards_to_create:
                Flashcard.objects.bulk_create(cards_to_create)
                
        return flashcard_set

    def update(self, instance, validated_data):
        cards_data = validated_data.pop('cards', None)
        instance.title = validated_data.get('title', instance.title).strip()
        instance.description = validated_data.get('description', instance.description).strip()
        instance.save()

        # If cards are provided in update, update/sync them
        if cards_data is not None:
            with transaction.atomic():
                existing_cards = {card.id: card for card in instance.cards.all()}
                kept_ids = []
                for idx, item in enumerate(cards_data):
                    card_id = item.get('id')
                    if card_id and card_id in existing_cards:
                        card = existing_cards[card_id]
                        card.term = item['term']
                        card.definition = item['definition']
                        card.order = idx
                        card.save()
                        kept_ids.append(card_id)
                    else:
                        new_card = Flashcard.objects.create(
                            set=instance,
                            term=item['term'],
                            definition=item['definition'],
                            order=idx
                        )
                        kept_ids.append(new_card.id)
                # Delete removed cards
                instance.cards.exclude(id__in=kept_ids).delete()

        return instance
