from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipes.serializers import RecipeSerializer


RECIPE_URL = reverse("recipes:")


def sample_user(username="test@gmail.com", password="passtest"):
    return get_user_model().objects.create(username=username, password=password)
    
