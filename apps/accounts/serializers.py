from rest_framework import serializers
from django.contrib.auth import get_user_model

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
            raise serializers.ValidationError("Имя пользователя обязательно.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Это имя пользователя уже занято.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Email обязателен.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email уже зарегистрирован.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают."})
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
            raise serializers.ValidationError({"username_or_email": "Email или имя пользователя обязательно."})
        if not password:
            raise serializers.ValidationError({"password": "Пароль обязателен."})

        # Try to find by email or username
        user = None
        if '@' in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        if not user:
            user = User.objects.filter(username__iexact=identifier).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({"non_field_errors": "Неверный email/имя пользователя или пароль."})

        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": "Этот аккаунт отключён."})

        attrs['user'] = user
        return attrs

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    confirm_password = serializers.CharField(required=False, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Текущий пароль указан неверно.")
        return value

    def validate(self, attrs):
        if attrs.get('confirm_password') and attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Новые пароли не совпадают."})
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "Новый пароль должен отличаться от текущего."})
        return attrs
