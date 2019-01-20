from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_create_user_without_name_fail(self):
        payload = {
            'email': 'foo@bar.gr',
            'password': 'password',
        }
        resp = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_retrieve_profile_without_authentication(self):
        resp = self.client.get(ME_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(APITestCase):

    def setUp(self):
        self.user = create_user(
            email='foo@bar.gr',
            password='tes1234',
            name='Pete Papadopoulos'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        resp = self.client.get(ME_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_update_profile_with_method_patch_success(self):
        payload = {
            'email': 'new@mail.com',
        }
        resp = self.client.patch(ME_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload['email'])

    def test_update_profile_with_method_put_success(self):
        payload = {
            'email': 'new@mail.com',
            'password': 'newpassword123',
            'name': 'New Name'
        }
        resp = self.client.put(ME_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])

    def test_update_profile_with_method_put_partial_fail(self):
        payload = {
            'email': 'new@mail.com',
            'password': 'newpassword123',
        }
        resp = self.client.put(ME_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(self.user.email, payload['email'])
        self.assertFalse(self.user.check_password(payload['email']))

    def test_update_profile_with_method_post(self):
        resp = self.client.post(ME_URL, {})

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
