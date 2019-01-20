from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(APITestCase):

    def test_create_user_success(self):
        payload = {
            'email': 'foo@bar.gr',
            'password': 'password',
            'name': 'Test user'
        }
        resp = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**resp.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', resp.data)
        self.assertEqual(resp.data['name'], payload['name'])

    def test_create_user_without_name_success(self):
        payload = {
            'email': 'foo@bar.gr',
            'password': 'password',
        }
        resp = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**resp.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', resp.data)
        self.assertIsNone(resp.data['name'])

    def test_create_user_already_exists(self):
        payload = {
            'email': 'foo@bar.gr',
            'password': 'password'
        }
        create_user(**payload)
        resp = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            'email': 'foo@bar.gr',
            'password': 'pw'
        }
        resp = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_create_token_success(self):
        payload = {
            'email': 'foo@bar.gr',
            'password': 'testpassword'
        }
        create_user(**payload)
        resp = self.client.post(TOKEN_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_token_wrong_password(self):
        create_user(email='foo@bar.gr', password='testpassword')
        payload = {
            'email': 'foo@bar.gr',
            'password': 'wrong'
        }
        resp = self.client.post(TOKEN_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        payload = {
            'email': 'foo@bar.gr',
            'password': 'testpassword'
        }
        resp = self.client.post(TOKEN_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_empty_password(self):
        create_user(email='foo@bar.gr', password='wrong')
        payload = {
            'email': 'foo@bar.gr',
            'password': ''
        }
        resp = self.client.post(TOKEN_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_wrong_email_format(self):
        create_user(email='foo@bar.gr', password='wrong')
        payload = {
            'email': 'foo.bar.gr',
            'password': 'test123'
        }
        resp = self.client.post(TOKEN_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
