from django.urls import path
from .views import (
    FlashcardSetListCreateView,
    FlashcardSetDetailView,
    FlashcardListCreateView,
    FlashcardDetailView
)

urlpatterns = [
    path('sets/', FlashcardSetListCreateView.as_view(), name='set_list_create'),
    path('sets/<int:pk>/', FlashcardSetDetailView.as_view(), name='set_detail'),
    path('sets/<int:set_id>/cards/', FlashcardListCreateView.as_view(), name='set_cards_list_create'),
    path('cards/<int:pk>/', FlashcardDetailView.as_view(), name='card_detail'),
]
