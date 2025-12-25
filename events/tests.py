from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Event


class EventAlertCreationTest(TestCase):
    """Test that HIGH severity events automatically create alerts"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_high_severity_event_creates_alert(self):
        """Test that creating a HIGH severity event automatically creates an alert"""
        from alerts.models import Alert
        
        # Create HIGH severity event
        event = Event.objects.create(
            source_name='Firewall',
            event_type='Intrusion Attempt',
            severity='HIGH',
            description='Unauthorized access attempt detected'
        )
        
        # Verify alert was created
        alert = Alert.objects.get(event=event)
        self.assertEqual(alert.severity, 'HIGH')
        self.assertEqual(alert.status, 'OPEN')
        self.assertEqual(alert.title, 'Alert: Intrusion Attempt')
        self.assertEqual(alert.description, 'Unauthorized access attempt detected')

    def test_critical_severity_event_creates_alert(self):
        """Test that creating a CRITICAL severity event automatically creates an alert"""
        from alerts.models import Alert
        
        # Create CRITICAL severity event
        event = Event.objects.create(
            source_name='IDS',
            event_type='Data Breach',
            severity='CRITICAL',
            description='Sensitive data exfiltration detected'
        )
        
        # Verify alert was created
        alert = Alert.objects.get(event=event)
        self.assertEqual(alert.severity, 'CRITICAL')
        self.assertEqual(alert.status, 'OPEN')

    def test_low_severity_event_does_not_create_alert(self):
        """Test that LOW severity events do not create alerts"""
        from alerts.models import Alert
        
        initial_alert_count = Alert.objects.count()
        
        # Create LOW severity event
        Event.objects.create(
            source_name='Firewall',
            event_type='Connection',
            severity='LOW',
            description='Normal connection'
        )
        
        # Verify no alert was created
        self.assertEqual(Alert.objects.count(), initial_alert_count)


class EventPermissionTest(TestCase):
    """Test event creation permissions"""

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
        
        # Create API clients
        self.admin_client = APIClient()
        self.analyst_client = APIClient()

    def _get_token(self, user):
        """Helper method to get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_analyst_cannot_create_event(self):
        """Test that Analyst cannot create events (403 Forbidden)"""
        token = self._get_token(self.analyst_user)
        self.analyst_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.analyst_client.post(
            '/api/events/',
            {
                'source_name': 'Firewall',
                'event_type': 'Intrusion Attempt',
                'severity': 'HIGH',
                'description': 'Unauthorized access attempt'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_event(self):
        """Test that Admin can create events"""
        token = self._get_token(self.admin_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.admin_client.post(
            '/api/events/',
            {
                'source_name': 'Firewall',
                'event_type': 'Intrusion Attempt',
                'severity': 'HIGH',
                'description': 'Unauthorized access attempt'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
