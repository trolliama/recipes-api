from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe

from recipes.serializers import TagSerializer

TAG_URL = reverse("recipes:tag-list")


def sample_user(email="sample@gmail.com", password="pass1234test"):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTestTagsApi(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_require_authentication(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestTagsApi(TestCase):
    def setUp(self):
        self.user = sample_user()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_tags(self):
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_tags_listed(self):
        # Second user for test (shouldn't return this tag)
        second_user_tag = Tag.objects.create(
            user=sample_user(email="second@gmail.com"), name="Dinner"
        )

        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)
        user_tags = Tag.objects.filter(user=self.user)

        serializer = TagSerializer(user_tags, many=True)

        # The second tag will be the second_user_tag because it's ordered
        self.assertNotEqual(second_user_tag.name, res.data[1]["name"])
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_tag_endpoint_sucess(self):
        payload = {"name": "new tag"}
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user, name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_endpoint_invalid(self):
        payload = {"name": ""}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            title="Coriander eggs on toast",
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAG_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title="Pancakes", time_minutes=5, price=3.00, user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title="Porridge", time_minutes=3, price=2.00, user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAG_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
