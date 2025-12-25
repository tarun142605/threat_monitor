from django.db import models
from django.core.exceptions import ValidationError


class Alert(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Database-level constraint: exactly one alert per event
        constraints = [
            models.UniqueConstraint(
                fields=['event'],
                name='unique_alert_per_event',
                condition=models.Q(event__isnull=False)
            )
        ]
        # Keep unique_together for backward compatibility and Django admin
        unique_together = [['event']]

    def clean(self):
        """Application-level validation to prevent duplicate alerts"""
        if self.event:
            # Check if another alert already exists for this event
            existing_alert = Alert.objects.filter(event=self.event).exclude(pk=self.pk).first()
            if existing_alert:
                raise ValidationError({
                    'event': f'An alert already exists for this event (Alert ID: {existing_alert.id}). Only one alert per event is allowed.'
                })

    def save(self, *args, **kwargs):
        """Override save to enforce validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title