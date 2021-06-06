from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="sample@gmail.com", password="pass1234test"):
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def test_create_user_with_email_succesful(self):
        email = "test@londonapp.com"
        password = "test1234"

        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_email_field_to_lower_succesful(self):
        email = "test@EMAIL.COM"
        password = "test1234"

        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_email_raises_value_error_with_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "1233456")

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            "superuser@email.com", "testysysy"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_creation_user(self):
        tag = models.Tag.objects.create(name="vegan", user=sample_user())

        print("tag: ", tag)
        self.assertEqual(str(tag), tag.name)

    def test_str_ingredient_model(self):
        ingredient = models.Ingredient.objects.create(
            name="Carrot", user=sample_user()
        )

        self.assertEqual("Carrot", str(ingredient))

    def test_str_recipe_model(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Steak and mushroom sauce",
            time_minutes=5,
            price=5.00,
        )

        self.assertEqual(recipe.title, str(recipe))
