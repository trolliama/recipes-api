from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

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
