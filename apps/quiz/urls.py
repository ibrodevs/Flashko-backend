from django.urls import path
from .views import (
    QuizStartView,
    QuizAnswerView,
    QuizDetailView,
    QuizFinishView,
    QuizDiscardView
)

urlpatterns = [
    path('start/', QuizStartView.as_view(), name='quiz_start'),
    path('<int:session_id>/answer/', QuizAnswerView.as_view(), name='quiz_answer'),
    path('<int:session_id>/finish/', QuizFinishView.as_view(), name='quiz_finish'),
    path('<int:session_id>/discard/', QuizDiscardView.as_view(), name='quiz_discard'),
    path('<int:session_id>/', QuizDetailView.as_view(), name='quiz_detail'),
]

