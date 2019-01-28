from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from core.models import Recipe
from recipe.serializer import RecipeSerializer

RECIPE_LIST_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe',
        'price': 5.00,
        'time_minutes': 10
    }

    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(APITestCase):

    def test_retrieve_recipe(self):
        resp = self.client.get(RECIPE_LIST_URL)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'foo@bar.gr',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        sample_recipe(self.user)
        sample_recipe(self.user)
        recipes = Recipe.objects.order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        resp = self.client.get(RECIPE_LIST_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_retrieve_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'another@bar.gr',
            'test123'
        )
        sample_recipe(self.user)
        sample_recipe(user2)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        resp = self.client.get(RECIPE_LIST_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)
