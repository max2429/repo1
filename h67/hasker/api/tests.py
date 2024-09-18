# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from askme.models import Question
import json


User = get_user_model()

API_QUESTION_LIST = reverse('api:question-list')
API_TOKEN_AUTH = reverse('api:token_obtain_pair')
API_TOKEN_REFRESH = reverse('api:token_refresh')
API_TOKEN_VERIFY = reverse('api:token_verify')

BAD_TOKEN = 'BAD_TOKEN'
USERNAME = 'user'
USER_PASSWORD = 'password'

credentials = {
    'username': USERNAME,
    'password': USER_PASSWORD
}

credentials2 = {
    'username': 'user1',
    'password': 'pass1'
}


def create_test_user():
    user = User.objects.create_user(USERNAME, 'test@test.com', USER_PASSWORD)


def create_test_user2():
    user = User.objects.create_user('user1', 'test@test.com', 'pass1')
    return user


def obtain_token(credentials):
    client = APIClient()
    resp = client.post(API_TOKEN_AUTH, credentials, format='json')
    token_access, token_refresh = json.loads(resp._container[0].decode("utf-8"))["access"],json.loads(resp._container[0].decode("utf-8"))["refresh"]
    return token_access, token_refresh


def obtain_token2():
    client = APIClient()
    resp = client.post(API_TOKEN_AUTH, credentials2, format='json')
    return resp.token


class JWTAuth(APITestCase):
    def setUp(self):
        self.user = create_test_user()

    def test_obtain_token(self):
        token_access,token_refresh = obtain_token(credentials)
        self.assertTrue(len(token_access) > 0)

    def test_refresh_token(self):
        token_access,token_refresh = obtain_token(credentials)
        resp = self.client.post(API_TOKEN_REFRESH, {'access': token_access, 'refresh': token_refresh}, format='json')
        new_token = resp.json()['access']
        self.assertTrue(len(new_token) > 0)
        self.assertNotEqual(token_access, new_token)

    def test_verify_token(self):
        token_acc,token_ref = obtain_token(credentials)
        resp = self.client.post(API_TOKEN_VERIFY, {'token': token_acc}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_verify_bad_token(self):
        resp = self.client.post(API_TOKEN_VERIFY, {'token': BAD_TOKEN}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)



class QuestionsAPI(APITestCase):
    questions_raw = [
        {'title': 'title_1', 'text': 'text_1'},
        {'title': 'title_2', 'text': 'text_2'},
        {'title': 'title_3', 'text': 'text_3'},
    ]

    def setUp(self):
        self.user = create_test_user2()
        #print(f"vars(user)={vars(self.user)}")
        for q in self.questions_raw:
            Question.objects.create(title=q['title'], text=q['text'], user=self.user)

    def test_unauthorized_401(self):
        resp = self.client.get(API_QUESTION_LIST)
        #print(f"status_code={resp.status_code}")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_user_can_get_list(self):
        token_acc,token_ref = obtain_token(credentials2)
        self.client.force_authenticate(self.user)
        resp = self.client.get(API_QUESTION_LIST)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        questions_count = resp.json()['count']
        self.assertEqual(questions_count, Question.objects.count())

    def test_create_question(self):
        token_acc,token_ref = obtain_token(credentials2)
        self.client.force_authenticate(self.user)
        resp = self.client.post(API_QUESTION_LIST, {'title': 'title_4', 'text': 'text_4'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(self.questions_raw) + 1, Question.objects.count())

