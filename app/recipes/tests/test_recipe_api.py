import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, TransactionTestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipes.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse("recipes:recipe-list")


def image_upload_url(recipe_id):
    return reverse("recipes:recipe-upload-image", args=[recipe_id])


def recipe_detail(recipe_id):
    return reverse("recipes:recipe-detail", args=[recipe_id])


def sample_tag(user, name="Test tag"):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Sample ingredient"):
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        recipe = sample_recipe(self.user)

        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        url = recipe_detail(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        payload = {"title": "Basic Recipe", "time_minutes": 5, "price": 5.00}
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")
        payload = {
            "title": "Test Recipe",
            "tags": [tag1.id, tag2.id],
            "time_minutes": 5,
            "price": 30.00,
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(user=self.user, name="Carrot")
        ingredient2 = sample_ingredient(user=self.user, name="Apple")
        payload = {
            "title": "Test Recipe",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 5,
            "price": 30.0,
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        recipe = sample_recipe(self.user)

        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        new_tag = sample_tag(user=self.user, name="Vegan")
        payload = {"title": "New Updated Title", "tags": [new_tag.id]}

        url = recipe_detail(recipe.id)
        self.client.patch(url, payload)

        updated_recipe = Recipe.objects.get(id=recipe.id)
        tags = recipe.tags.all()

        self.assertEqual(updated_recipe.title, payload["title"])
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)
        self.assertEqual(updated_recipe.price, recipe.price)

    def test_full_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            "title": "Spaghetti carbonara",
            "time_minutes": 25,
            "price": 5.00,
        }
        url = recipe_detail(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.price, payload["price"])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTest(TransactionTestCase):
    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()

        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_valid_image(self):
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image(self):
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {"image": "ntf"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        recipe1 = sample_recipe(user=self.user, title="Thai vegetable curry")
        recipe2 = sample_recipe(user=self.user, title="Aubergine with tahini")
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Vegetarian")
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title="Fish and chips")

        res = self.client.get(RECIPE_URL, {"tags": f"{tag1.id},{tag2.id}"})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        recipe1 = sample_recipe(user=self.user, title="Posh beans on toast")
        recipe2 = sample_recipe(user=self.user, title="Chicken cacciatore")
        ingredient1 = sample_ingredient(user=self.user, name="Feta cheese")
        ingredient2 = sample_ingredient(user=self.user, name="Chicken")
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title="Steak and mushrooms")

        res = self.client.get(
            RECIPE_URL, {"ingredients": f"{ingredient1.id},{ingredient2.id}"}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
