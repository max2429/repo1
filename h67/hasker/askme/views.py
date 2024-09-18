# -*- coding: utf-8 -*-
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, RedirectView, View
from django.urls import reverse_lazy
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import QuestionForm
from .models import Question, Tag, Answer


class QuestionVoteUpView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs['question_id'])
        question.vote_up(request.user.id)
        return JsonResponse({'votes': question.votes})


class QuestionVoteDownView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, pk=kwargs['question_id'])
        question.vote_down(request.user.id)
        return JsonResponse({'votes': question.votes})


class AnswerCreateView(LoginRequiredMixin, CreateView):
    model = Answer
    fields = ['text']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question = get_object_or_404(Question, slug=self.kwargs.get('slug'))
        return super().form_valid(form)

    def get_success_url(self):
        question_slug = self.kwargs.get('slug')
        return reverse_lazy('askme:question', kwargs={'slug': question_slug})


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'askme/question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answer_list = self.object.answer_set.all().order_by('-votes')
        page = self.request.GET.get('page')
        context['answers'] = self.paginate_queryset(answer_list, page, 30)
        return context

    def paginate_queryset(self, queryset, page, per_page=20):
        paginator = Paginator(queryset, per_page)
        try:
            paginated_list = paginator.page(page)
        except PageNotAnInteger:
            paginated_list = paginator.page(1)
        except EmptyPage:
            paginated_list = paginator.page(paginator.num_pages)
        return paginated_list


class IndexView(ListView):
    model = Question
    template_name = 'askme/index.html'
    context_object_name = 'questions'
    paginate_by = 20
    ordering = ['-date_pub', '-votes']


class AskView(LoginRequiredMixin, CreateView):
    form_class = QuestionForm
    template_name = 'askme/ask.html'
    success_url = reverse_lazy('askme:index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AskView, self).form_valid(form)


class QuestionBySlugView(DetailView):
    model = Question
    template_name = 'askme/question.html'
    context_object_name = 'question'
    slug_url_kwarg = 'slug'

    def paginate_queryset(self, queryset, page, per_page=20):
        paginator = Paginator(queryset, per_page)
        try:
            paginated_list = paginator.page(page)
        except PageNotAnInteger:
            paginated_list = paginator.page(1)
        except EmptyPage:
            paginated_list = paginator.page(paginator.num_pages)
        return paginated_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answer_list = self.object.answer_set.all().order_by('-votes')
        page = self.request.GET.get('page')
        context['answers'] = self.paginate_queryset(answer_list, page, 30)
        return context


class SearchTagView(ListView):
    template_name = 'askme/search.html'
    context_object_name = 'questions'

    def get_queryset(self):
        tag_name = self.kwargs.get('tag_name')
        tag = Tag.objects.filter(name=tag_name).first()
        if tag:
            return tag.question_set.all()
        return Question.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'head_title': 'Tag results',
            'search_query': f'tag:{self.kwargs.get("tag_name")}'
        })
        return context


class SearchView(ListView):
    template_name = 'askme/search.html'
    context_object_name = 'questions'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if len(query) > 100:
            return Question.objects.none()
        return Question.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        ).order_by('-date_pub', '-votes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['head_title'] = 'Search results'
        return context


class AnswerVoteUpView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        answer_id = kwargs.get('answer_id')
        answer = get_object_or_404(Answer, pk=answer_id)
        user_id = request.user.pk
        answer.vote_up(user_id)
        return JsonResponse({'votes': answer.votes})

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('askme:question', kwargs={'slug': self.kwargs.get('slug')})


class AnswerVoteDownView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        answer_id = kwargs.get('answer_id')
        answer = get_object_or_404(Answer, pk=answer_id)
        user_id = request.user.pk
        answer.vote_down(user_id)
        return HttpResponse(answer.votes)


class SetCorrectAnswerView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        answer_id = kwargs.get('answer_id')
        answer = get_object_or_404(Answer, pk=answer_id)
        if answer.question.user.pk == request.user.pk:
            with transaction.atomic():
                answer.question.correct_answer = answer
                answer.question.save()
            return JsonResponse({'correct_answer_id': answer.pk})
        else:
            return HttpResponseBadRequest('Not allowed')


def today():
   today = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
   return today

