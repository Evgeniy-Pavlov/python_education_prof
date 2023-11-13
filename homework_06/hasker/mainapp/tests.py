import json
from http import HTTPStatus
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from .models import UserBase, Question, Reply


# Create your tests here.
class QuestionGetAPITests(APITestCase):

    def setUp(self):
        self.user_1 = UserBase.objects.create(username='questions_user_1', email='test_user_1@mail.com')
        self.user_2 = UserBase.objects.create(username='questions_user_2', email='test_user_2@mail.com')
        for i in range(5):
            Question.objects.create(user_create=self.user_1, header=f'test header {i+1}', body=f'test body {i+1}')
            Question.objects.create(user_create=self.user_2, header=f'test header {i+1}', body=f'test body {i+1}')
        
    def test_get_questions(self):
        response = self.client.get('/api/v1/questions/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_content = json.loads(response.content)
        self.assertEqual(list(response_content), ['count', 'next', 'previous', 'results'])
        self.assertEqual(len(response_content['results']), 10)
        self.assertEqual(list(response_content['results'][0]), ['id', 'header', 'body', 'date_create', 'user_create_id', 'username', 'votes'])
        self.assertTrue(isinstance(response_content['results'][0]['id'], int))
        self.assertTrue(isinstance(response_content['results'][0]['header'], str))
        self.assertTrue(isinstance(response_content['results'][0]['body'], str))
        self.assertTrue(isinstance(response_content['results'][0]['username'], str))
        self.assertTrue(isinstance(response_content['results'][0]['votes'], int))
        self.assertTrue(isinstance(response_content['results'][0]['user_create_id'], int))
        self.assertTrue(isinstance(response_content['results'][0]['date_create'], str))
    
    def test_get_success_question(self):
        results = [self.client.get(f'/api/v1/question/{x+1}') for x in range(10)]
        for response in results:
            self.assertEqual(response.status_code, HTTPStatus.OK)
            response_content = json.loads(response.content)
            self.assertEqual(list(response_content), ['id', 'header', 'body', 'date_create', 'user_create', 'username', 'votes', 'tags'])
            self.assertTrue(isinstance(response_content['id'], int))
            self.assertTrue(isinstance(response_content['header'], str))
            self.assertTrue(isinstance(response_content['body'], str))
            self.assertTrue(isinstance(response_content['username'], str))
            self.assertTrue(isinstance(response_content['user_create'], int))
            self.assertTrue(isinstance(response_content['votes'], int))
            self.assertTrue(isinstance(response_content['date_create'], str))
            self.assertTrue(isinstance(response_content['tags'], list))

    def test_get_failed_question(self):
        response = self.client.get(f'/api/v1/question/0')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response_content = json.loads(response.content)
        self.assertEqual(response_content, {"error": "Question not found."})

    def test_get_search_question(self):
        response = self.client.get(f'/api/v1/questions/search?strng=test body')
        response_content = json.loads(response.content)
        self.assertEqual(len(response_content), 10)
        for question in response_content:
            self.assertEqual(list(question), ['id', 'header', 'user_create__logo', 'user_create__username', 'date_create', 'votes'])
            self.assertTrue(isinstance(question['id'], int))
            self.assertTrue(isinstance(question['header'], str))
            self.assertTrue(isinstance(question['user_create__logo'], str))
            self.assertTrue(isinstance(question['user_create__username'], str))
            self.assertTrue(isinstance(question['date_create'], str))
            self.assertTrue(isinstance(question['votes'], int))

    def test_get_questions_trending(self):
        response = self.client.get(f'/api/v1/questions/trending')
        response_content = json.loads(response.content)
        self.assertEqual(len(response_content), 10)
        for question in response_content:
            self.assertEqual(list(question), ['id', 'header', 'body', 'user_create', 'user_create__username', 'date_create', 'votes'])
            self.assertTrue(isinstance(question['id'], int))
            self.assertTrue(isinstance(question['header'], str))
            self.assertTrue(isinstance(question['body'], str))
            self.assertTrue(isinstance(question['user_create'], int))
            self.assertTrue(isinstance(question['user_create__username'], str))
            self.assertTrue(isinstance(question['date_create'], str))
            self.assertTrue(isinstance(question['votes'], int))


class ReplyGetAPITests(APITestCase):

    def setUp(self):
        self.user_1 = UserBase.objects.create(username='questions_user_1', email='test_user_1@mail.com')
        self.user_2 = UserBase.objects.create(username='questions_user_2', email='test_user_2@mail.com')
        self.question_1 = Question.objects.create(user_create=self.user_1, header=f'test header 1', body=f'test body 1')
        self.question_2 = Question.objects.create(user_create=self.user_2, header=f'test header 2', body=f'test body 2')
        for i in range(5):
            Reply.objects.create(question=self.question_1, user_create=self.user_2, text=f'text comment {i}')
            Reply.objects.create(question=self.question_2, user_create=self.user_1, text=f'text comment {i}')

    def test_get_reply(self):
        results = [self.client.get(f'/api/v1/question/{x+1}/reply') for x in range(2)]
        for response in results:
            self.assertEqual(response.status_code, HTTPStatus.OK)
            response_content = json.loads(response.content)
            for item in response_content:
                self.assertEqual(list(item), ['id', 'text', 'best_reply', 'user_create_id', 'question_id', 'date_create', 'user_create_id__username', 'rating'])
                self.assertTrue(isinstance(item['id'], int))
                self.assertTrue(isinstance(item['text'], str))
                self.assertTrue(isinstance(item['best_reply'], bool))
                self.assertTrue(isinstance(item['user_create_id'], int))
                self.assertTrue(isinstance(item['question_id'], int))
                self.assertTrue(isinstance(item['date_create'], str))
                self.assertTrue(isinstance(item['user_create_id__username'], str))
                self.assertTrue(isinstance(item['rating'], int))



