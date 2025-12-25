from rest_framework import serializers
from django.utils.html import strip_tags
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(source='event.id', read_only=True)
    event_type = serializers.CharField(source='event.event_type', read_only=True)
    severity = serializers.CharField(source='event.severity', read_only=True)
    # Ensure sensitive fields are read-only
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'title', 'description', 'severity', 'status', 'event_id', 'event_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'title', 'description', 'created_at', 'updated_at']


class AlertStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating alert status - Admin only"""
    
    status = serializers.ChoiceField(
        choices=Alert.STATUS_CHOICES,
        error_messages={
            'invalid_choice': 'Status must be one of: OPEN, ACKNOWLEDGED, RESOLVED'
        }
    )
    
    class Meta:
        model = Alert
        fields = ['status']
    
    def validate_status(self, value):
        """Validate that status can only be changed to ACKNOWLEDGED or RESOLVED"""
        if not value:
            raise serializers.ValidationError('Status is required.')
        allowed_statuses = ['ACKNOWLEDGED', 'RESOLVED']
        # Normalize to uppercase
        value_upper = value.upper()
        if value_upper not in allowed_statuses:
            raise serializers.ValidationError(
                f'Status can only be changed to: {", ".join(allowed_statuses)}'
            )
        return value_upper
