from django.test import TestCase
from django.contrib.auth.models import User, Group
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
