from django.urls import path
from .views import (
    APIRootView,
    QuestionListView,
    QuestionDetailView,
    AnswerListView,
    TopQuestionListView,
    SearchListView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

app_name = 'api'

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:pk>/answers/', AnswerListView.as_view(), name='answer-list'),
    path('trending/', TopQuestionListView.as_view(), name='trending-list'),
    path('search/', SearchListView.as_view(), name='search-list'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]