from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    sets_count = serializers.SerializerMethodField()
    cards_count = serializers.SerializerMethodField()
    quiz_sessions_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at', 'sets_count', 'cards_count', 'quiz_sessions_count']
        read_only_fields = ['id', 'created_at', 'sets_count', 'cards_count', 'quiz_sessions_count']

    def get_sets_count(self, obj):
        return obj.sets.count()

    def get_cards_count(self, obj):
        from apps.flashcards.models import Flashcard
        return Flashcard.objects.filter(set__user=obj).count()

    def get_quiz_sessions_count(self, obj):
        return obj.quiz_sessions.count()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=6)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Username is required.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        identifier = attrs.get('username_or_email', '').strip()
        password = attrs.get('password', '')

        if not identifier:
            raise serializers.ValidationError({"username_or_email": "Email or username is required."})
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        # Try to find by email or username
        user = None
        if '@' in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        if not user:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({"non_field_errors": "Invalid email/username or password."})

        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": "This account is disabled."})

        attrs['user'] = user
        return attrs
