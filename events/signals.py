from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger('events')


@receiver(post_save, sender='events.Event')
def create_alert_for_high_severity_event(sender, instance, created, **kwargs):
    """
    Automatically create an Alert when a NEW Event with HIGH or CRITICAL severity is created.
    
    Guarantees:
    - Alert is created ONLY when a new Event is created (not on updates)
    - Severity must be HIGH or CRITICAL
    - Exactly ONE alert per event is allowed
    - No duplicate alerts can be created under any condition
    
    Enforced at:
    - Database level: UniqueConstraint on event field
    - Application level: Validation in Alert model and signal logic
    """
    # CRITICAL: Only process NEW events, not updates
    if not created:
        return
    
    # CRITICAL: Only process HIGH or CRITICAL severity events
    if instance.severity not in ['HIGH', 'CRITICAL']:
        return
    
    # Import here to avoid circular import
    from alerts.models import Alert
    
    # Use atomic transaction to ensure consistency
    try:
        with transaction.atomic():
            # Check if alert already exists for this event (defensive check)
            existing_alert = Alert.objects.filter(event=instance).first()
            if existing_alert:
                logger.warning(
                    f'Alert already exists for event {instance.id}. '
                    f'Skipping alert creation to prevent duplicate. Existing alert ID: {existing_alert.id}'
                )
                return
            
            # Create alert atomically
            # get_or_create ensures idempotency and handles race conditions
            alert, created_alert = Alert.objects.get_or_create(
                event=instance,
                defaults={
                    'title': f"Alert: {instance.event_type}",
                    'description': instance.description,
                    'severity': instance.severity,
                    'status': 'OPEN',
                }
            )
            
            if created_alert:
                logger.info(
                    f'Auto-created alert {alert.id} for event {instance.id} '
                    f'(severity: {instance.severity}, type: {instance.event_type})'
                )
            else:
                logger.warning(
                    f'Alert {alert.id} already exists for event {instance.id}. '
                    f'This should not happen due to database constraints.'
                )
                
    except IntegrityError as e:
        # Database constraint violation - alert already exists
        logger.error(
            f'Database integrity error creating alert for event {instance.id}: {e}. '
            f'This indicates a duplicate alert attempt was prevented by database constraint.'
        )
        # Re-raise to ensure transaction rollback
        raise
    except ValidationError as e:
        # Application-level validation failed
        logger.error(
            f'Validation error creating alert for event {instance.id}: {e}'
        )
        raise
    except Exception as e:
        # Unexpected error - log and re-raise
        logger.error(
            f'Unexpected error creating alert for event {instance.id}: {e}',
            exc_info=True
        )
        raise
