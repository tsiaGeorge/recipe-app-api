from django.contrib.auth import get_user_model
from rest_framework import status

from core.models import Ingredient
from recipe.serializer import IngredientSerializer
from django.urls import reverse
from rest_framework.test import APITestCase


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITests(APITestCase):

    def test_unauthenticated(self):
        resp = self.client.get(INGREDIENT_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user('foo@bar.gr', 'pass123')
        self.client.force_authenticate(self.user)
        # self.client.force_login(user)

    def test_get_ingredients(self):
        Ingredient.objects.create(name='Vinegar', user=self.user)
        Ingredient.objects.create(name='Tomato', user=self.user)

        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        resp = self.client.get(INGREDIENT_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_get_ingredients_limit_to_user(self):
        other_user = get_user_model().objects.create_user(
            email='other@user.gr',
            password='pass123'
        )
        Ingredient.objects.create(name='Vinegar', user=self.user)
        Ingredient.objects.create(name='Tomato', user=other_user)
        ingredients = Ingredient.objects.filter(
            user=self.user
        ).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        resp = self.client.get(INGREDIENT_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_create_ingredient_api(self):
        resp = self.client.post(INGREDIENT_URL, data={'name': 'Apple'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_ingredient_api_invalid_name(self):
        resp = self.client.post(INGREDIENT_URL, data={'name': ''})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
