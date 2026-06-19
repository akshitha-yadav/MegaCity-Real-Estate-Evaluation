from django.test import TestCase, Client
from django.urls import reverse
from .models import UserPrediction


class UserViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

    # ------------------ Test Home Page ------------------
    def test_userhome_view(self):
        response = self.client.get(reverse('userhome'))
        self.assertEqual(response.status_code, 200)

    # ------------------ Test Prediction Page Load ------------------
    def test_userpredict_get(self):
        response = self.client.get(reverse('userpredict'))
        self.assertEqual(response.status_code, 200)

    # ------------------ Test Prediction POST ------------------
    def test_userpredict_post_valid(self):
        # Dummy input (adjust keys based on your form fields)
        data = {
            'feature_1': '10',
            'feature_2': '20',
            'feature_3': '30',
        }

        response = self.client.post(reverse('userpredict'), data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserPrediction.objects.exists())

    # ------------------ Test Invalid Input ------------------
    def test_userpredict_post_invalid(self):
        data = {
            'feature_1': 'abc',  # invalid numeric
            'feature_2': '',
        }

        response = self.client.post(reverse('userpredict'), data)

        self.assertEqual(response.status_code, 200)
        # Should not crash