from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from core.models import Recipe, Tag, Ingredient
from recipe.serializer import RecipeSerializer, RecipeDetailSerializer

RECIPE_LIST_URL = reverse('recipe:recipe-list')


def recipe_url_detail(_id):
    return reverse('recipe:recipe-detail', args=(_id, ))


def sample_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe',
        'price': 5.00,
        'time_minutes': 10
    }

    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, name='Sample Tag'):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Sample Ingredient'):
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        serializer = RecipeDetailSerializer(recipe)
        detail_url = recipe_url_detail(recipe.id)
        resp = self.client.get(detail_url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)
