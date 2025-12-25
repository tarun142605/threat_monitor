from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Event


@receiver(post_save, sender=Event)
def create_alert_for_high_severity_event(sender, instance, created, **kwargs):
    """
    Automatically create an Alert when an Event with HIGH or CRITICAL severity is created.
    Prevents duplicate alerts by using get_or_create which is atomic and handles race conditions.
    """
    if created and instance.severity in ['HIGH', 'CRITICAL']:
        # Import here to avoid circular import
        from alerts.models import Alert
        
        # Use get_or_create to prevent duplicates atomically
        # This ensures exactly one alert per event, even in concurrent scenarios
        with transaction.atomic():
            Alert.objects.get_or_create(
                event=instance,
                defaults={
                    'title': f"Alert: {instance.event_type}",
                    'description': instance.description,
                    'severity': instance.severity,
                    'status': 'OPEN',
                }
            )
