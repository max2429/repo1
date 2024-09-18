# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.postgres.search import SearchVector
from django.shortcuts import get_object_or_404

from askme.models import Question
from .serializers import QuestionSerializer, AnswerSerializer
from .permissions import IsOwner


class APIRootView(generics.GenericAPIView):
    name = 'api-root'

    def get(self, request):
        return Response({
            'questions': reverse_lazy('api:question-list', request=request),
            'trending': reverse_lazy('api:trending-list', request=request),
            'search': reverse_lazy('api:search-list', request=request),
        })


class QuestionListView(generics.ListCreateAPIView):
    queryset = Question.objects.all().order_by('-date_pub', '-votes')
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsOwner,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerListView(generics.ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question = get_object_or_404(Question, pk=self.kwargs.get('pk'))
        return question.answer_set.all()


class TopQuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.order_by('-votes')[:20]


class SearchListView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if len(query) > 100:
            query = ''
        queryset = Question.objects.annotate(
            search=SearchVector('title', 'text')
        ).filter(search=query).order_by('-date_pub', '-votes')
        return queryset
