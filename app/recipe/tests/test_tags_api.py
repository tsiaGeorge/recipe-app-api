from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Tag
from recipe.serializer import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(APITestCase):

    def test_login_required(self):
        resp = self.client.get(TAG_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'foo@bar.gr',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(name='Vegan', user=self.user)
        Tag.objects.create(name='Dessert', user=self.user)

        resp = self.client.get(TAG_URL)
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_tags_are_limited_to_user(self):
        other_user = get_user_model().objects.create_user(
            'another@user.gr', 'pass123'
        )
        Tag.objects.create(name='Vegan', user=self.user)
        Tag.objects.create(name='Dessert', user=self.user)
        Tag.objects.create(name='Fruity', user=other_user)

        resp = self.client.get(TAG_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        tags = Tag.objects.filter(user=self.user).order_by('-name')
        self.assertEqual(resp.data[0]['name'], tags[0].name)
        self.assertEqual(resp.data[1]['name'], tags[1].name)

    def test_tags_create_success(self):
        payload = {'name': 'Vegan'}
        resp = self.client.post(TAG_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['name'], payload['name'])

    def test_tags_invalid_fail(self):
        payload = {'name': ''}
        resp = self.client.post(TAG_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
