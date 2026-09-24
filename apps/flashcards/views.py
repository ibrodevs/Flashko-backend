from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FlashcardSet, Flashcard
from .serializers import (
    FlashcardSerializer,
    FlashcardSetListSerializer,
    FlashcardSetDetailSerializer,
    FlashcardSetCreateUpdateSerializer
)

class FlashcardSetListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sets = FlashcardSet.objects.filter(user=request.user).annotate(
            cards_count=Count('cards')
        ).order_by('-created_at')
        serializer = FlashcardSetListSerializer(sets, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FlashcardSetCreateUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            set_instance = serializer.save()
            # Return detail serializer with full cards
            detail_serializer = FlashcardSetDetailSerializer(set_instance, context={'request': request})
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FlashcardSetDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(FlashcardSet.objects.prefetch_related('cards'), pk=pk, user=user)

    def get(self, request, pk):
        set_instance = self.get_object(pk, request.user)
        serializer = FlashcardSetDetailSerializer(set_instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        set_instance = self.get_object(pk, request.user)
        serializer = FlashcardSetCreateUpdateSerializer(
            set_instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            updated_instance = serializer.save()
            detail_serializer = FlashcardSetDetailSerializer(updated_instance, context={'request': request})
            return Response(detail_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        set_instance = self.get_object(pk, request.user)
        set_instance.delete()
        return Response({'detail': 'Набор успешно удален.'}, status=status.HTTP_204_NO_CONTENT)

class FlashcardSetShareView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, share_id):
        set_instance = get_object_or_404(
            FlashcardSet.objects.prefetch_related('cards').select_related('user'),
            share_id=share_id,
            is_public=True
        )
        serializer = FlashcardSetDetailSerializer(set_instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class FlashcardSetCopyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, share_id):
        set_instance = get_object_or_404(
            FlashcardSet.objects.prefetch_related('cards'),
            share_id=share_id,
            is_public=True
        )
        
        with transaction.atomic():
            new_title = f"{set_instance.title} (копия)" if set_instance.user == request.user else set_instance.title
            new_set = FlashcardSet.objects.create(
                user=request.user,
                title=new_title,
                description=set_instance.description,
            )
            cards_to_copy = [
                Flashcard(
                    set=new_set,
                    term=card.term,
                    definition=card.definition,
                    order=card.order
                )
                for card in set_instance.cards.all()
            ]
            if cards_to_copy:
                Flashcard.objects.bulk_create(cards_to_copy)

        serializer = FlashcardSetDetailSerializer(new_set, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FlashcardListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, set_id):
        flashcard_set = get_object_or_404(FlashcardSet, pk=set_id, user=request.user)
        cards = flashcard_set.cards.all()
        serializer = FlashcardSerializer(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, set_id):
        flashcard_set = get_object_or_404(FlashcardSet, pk=set_id, user=request.user)
        serializer = FlashcardSerializer(data=request.data)
        if serializer.is_valid():
            last_order = flashcard_set.cards.count()
            card = serializer.save(set=flashcard_set, order=last_order)
            return Response(FlashcardSerializer(card).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FlashcardDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Flashcard.objects.select_related('set'), pk=pk, set__user=user)

    def patch(self, request, pk):
        card = self.get_object(pk, request.user)
        serializer = FlashcardSerializer(card, data=request.data, partial=True)
        if serializer.is_valid():
            updated_card = serializer.save()
            return Response(FlashcardSerializer(updated_card).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        card = self.get_object(pk, request.user)
        card.delete()
        return Response({'detail': 'Карточка успешно удалена.'}, status=status.HTTP_204_NO_CONTENT)
