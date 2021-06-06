from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipes.serializers import RecipeSerializer


RECIPE_URL = reverse("recipes:recipe-list")


def sample_recipe(user, **params):
    defaults = {
        "title": "Test Recipe Title",
        "time_minutes": 10,
        "price": 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def sample_user(email="test@gmail.com", password="passtest"):
    return get_user_model().objects.create(email=email, password=password)


class PublicRecipeTestApi(TestCase):
    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_list_recipes(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = sample_user(
            email="other@londonappdev.com", password="password123"
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
