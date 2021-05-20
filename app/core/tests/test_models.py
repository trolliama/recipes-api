from django.test import TestCase
from django.contrib.auth import get_user_model


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
