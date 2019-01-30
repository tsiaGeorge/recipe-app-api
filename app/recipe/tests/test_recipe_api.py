import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from core.models import Recipe, Tag, Ingredient
from recipe.serializer import RecipeSerializer, RecipeDetailSerializer

RECIPE_LIST_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=(recipe_id, ))


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

    def test_create_recipe(self):
        payload = {
            'title': 'Sample Recipe',
            'price': 4.00,
            'time_minutes': 5
        }

        resp = self.client.post(RECIPE_LIST_URL, payload)
        recipe = Recipe.objects.get(id=resp.data['id'])

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(self.user, 'sample tag1')
        tag2 = sample_tag(self.user, 'sample tag2')
        payload = {
            'title': 'Sample Recipe',
            'price': 4.00,
            'time_minutes': 5,
            'tags': [tag1.id, tag2.id]
        }
        resp = self.client.post(RECIPE_LIST_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(self.user, 'sample ingredient1')
        ingredient2 = sample_ingredient(self.user, 'sample ingredient2')
        payload = {
            'title': 'Sample Recipe',
            'price': 4.00,
            'time_minutes': 5,
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        resp = self.client.post(RECIPE_LIST_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')
        payload = {
            'title': 'Another Sample Url',
            'tags': [new_tag.id]
        }
        url = recipe_url_detail(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)

    def test_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        payload = {
            'title': 'Another Sample Url',
            'time_minutes': 5,
            'price': 5
        }
        url = recipe_url_detail(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.tags.count(), 0)
        self.assertEqual(recipe.ingredients.count(), 0)


class RecipeImageUploadTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@boo.gr', 'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))  # black square
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        recipe1 = sample_recipe(user=self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Vegetarian')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title='Fish and chips')

        resp = self.client.get(
            RECIPE_LIST_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, resp.data)
        self.assertIn(serializer2.data, resp.data)
        self.assertNotIn(serializer3.data, resp.data)

    def test_filter_by_ingredients(self):
        recipe1 = sample_recipe(user=self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')
        recipe3 = sample_recipe(user=self.user, title='Spaghetti with meat')
        ingredient1 = Ingredient.objects.create(user=self.user, name='Tomato')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Bean')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        resp = self.client.get(
            RECIPE_LIST_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, resp.data)
        self.assertIn(serializer2.data, resp.data)
        self.assertNotIn(serializer3.data, resp.data)
