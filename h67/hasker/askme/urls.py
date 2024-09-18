from django.urls import path
from .views import (
    IndexView,
    AskView,
    QuestionBySlugView,
    QuestionVoteUpView,
    QuestionVoteDownView,
    SearchTagView,
    SearchView,
    AnswerVoteUpView,
    AnswerVoteDownView,
    AnswerCreateView,
    SetCorrectAnswerView,
)

app_name = 'askme'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('ask/', AskView.as_view(), name='ask'),
    path('question/<slug:slug>/', QuestionBySlugView.as_view(), name='question'),
    path('question/<slug:slug>/answer/', AnswerCreateView.as_view(), name='answer_create'),
    path('tag/<str:tag_name>/', SearchTagView.as_view(), name='search_tag'),
    path('search/', SearchView.as_view(), name='search'),
    path('api_common/answer/voteup/<int:answer_id>/', AnswerVoteUpView.as_view(), name='answer_vote_up'),
    path('api_common/answer/votedown/<int:answer_id>/', AnswerVoteDownView.as_view(), name='answer_vote_down'),
    path('api_common/answer/setcorrect/<int:answer_id>/', SetCorrectAnswerView.as_view(), name='answer_set_correct'),
    path('api_common/question/voteup/<int:question_id>/', QuestionVoteUpView.as_view(), name='question_vote_up'),
    path('api_common/question/votedown/<int:question_id>/', QuestionVoteDownView.as_view(), name='question_vote_down'),
]
