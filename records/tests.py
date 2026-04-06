from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.settings import api_settings
from records.views import RecordViewSet
from users.models import User
from records.models import Record
from rest_framework_simplejwt.tokens import RefreshToken


def get_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class RecordAPITest(APITestCase):

    def setUp(self):
        # Disable throttling globally
        self.original_throttles = api_settings.DEFAULT_THROTTLE_CLASSES
        api_settings.DEFAULT_THROTTLE_CLASSES = []

        # ALSO disable view-level throttle
        self.original_view_throttle = RecordViewSet.throttle_classes
        RecordViewSet.throttle_classes = []

        # Users
        self.admin = User.objects.create_user(
            username='admin', password='admin123', role='admin'
        )
        self.viewer = User.objects.create_user(
            username='viewer', password='pass123', role='viewer'
        )

        self.url = "/api/records/"

    def tearDown(self):
        api_settings.DEFAULT_THROTTLE_CLASSES = self.original_throttles
        RecordViewSet.throttle_classes = self.original_view_throttle
    def test_auth_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_record(self):
        token = get_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        data = {
            "amount": 1000,
            "type": "income",
            "category": "salary",
            "date": "2026-04-06"
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewer_cannot_create(self):
        token = get_token(self.viewer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        data = {
            "amount": 500,
            "type": "expense",
            "category": "food",
            "date": "2026-04-06"
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_soft_delete(self):
        record = Record.objects.create(
            amount=100,
            type='income',
            category='salary',
            date='2026-04-06',
            created_by=self.admin
        )

        token = get_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.delete(f"{self.url}{record.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        record.refresh_from_db()
        self.assertTrue(record.is_deleted)

    def test_deleted_records_hidden(self):
        Record.objects.create(
            amount=100,
            type='income',
            category='salary',
            date='2026-04-06',
            created_by=self.admin,
            is_deleted=True
        )

        token = get_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(self.url)
        self.assertEqual(len(response.data['results']), 0)

    def test_record_throttle(self):
        # Re-enable throttling
        RecordViewSet.throttle_classes = self.original_view_throttle

        api_settings.DEFAULT_THROTTLE_CLASSES = self.original_throttles

        # IMPORTANT: reduce rate for test
        from django.conf import settings
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['records'] = '5/min'

        token = get_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        for _ in range(6):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)