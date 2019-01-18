from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_success(self):
        email = 'foo@bar.gr'
        password = 'test123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password, password)

    def test_create_user_with_normalize_email_success(self):
        email = 'foo@BAR.gr'
        password = 'test123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())
        self.assertTrue(user.check_password, password)

    def test_create_user_with_wrong_email_format(self):
        email = 'foo'
        password = 'test123'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password
            )

    def test_create_user_with_no_email(self):
        email = None
        password = 'test123'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password
            )

    def test_create_superuser(self):
        email = 'foo@bar.gr'
        password = 'test123'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
