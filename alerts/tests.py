from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from events.models import Event
from .models import Alert


class AlertStatusUpdatePermissionTest(TestCase):
    """Test alert status update permissions"""

    def setUp(self):
        """Set up test data"""
        # Create Admin user and group
        self.admin_group, _ = Group.objects.get_or_create(name='Admin')
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        self.admin_user.groups.add(self.admin_group)
        
        # Create Analyst user and group
        self.analyst_group, _ = Group.objects.get_or_create(name='Analyst')
        self.analyst_user = User.objects.create_user(
            username='analyst',
            password='analystpass123'
        )
        self.analyst_user.groups.add(self.analyst_group)
        
        # Create test event and alert
        self.event = Event.objects.create(
            source_name='Firewall',
            event_type='Intrusion Attempt',
            severity='HIGH',
            description='Unauthorized access attempt'
        )
        self.alert = Alert.objects.get(event=self.event)
        
        # Create API clients
        self.admin_client = APIClient()
        self.analyst_client = APIClient()

    def _get_token(self, user):
        """Helper method to get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_analyst_cannot_update_alert_status(self):
        """Test that Analyst cannot update alert status (403 Forbidden)"""
        token = self._get_token(self.analyst_user)
        self.analyst_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = f'/api/alerts/{self.alert.id}/'
        response = self.analyst_client.patch(
            url,
            {'status': 'ACKNOWLEDGED'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_alert_status(self):
        """Test that Admin can update alert status"""
        token = self._get_token(self.admin_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = f'/api/alerts/{self.alert.id}/'
        response = self.admin_client.patch(
            url,
            {'status': 'ACKNOWLEDGED'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'ACKNOWLEDGED')

    def test_admin_can_update_to_resolved(self):
        """Test that Admin can update alert status to RESOLVED"""
        token = self._get_token(self.admin_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = f'/api/alerts/{self.alert.id}/'
        response = self.admin_client.patch(
            url,
            {'status': 'RESOLVED'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'RESOLVED')
