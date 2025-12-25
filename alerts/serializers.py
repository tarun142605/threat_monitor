from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    # Derived fields from related Event (not in Alert model, but useful for API consumers)
    event_id = serializers.IntegerField(source='event.id', read_only=True)
    event_type = serializers.CharField(source='event.event_type', read_only=True)
    
    # Alert model fields - ensure sensitive fields are read-only
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    severity = serializers.CharField(read_only=True)  # Use Alert's own severity field

    class Meta:
        model = Alert
        fields = [
            # Alert model fields
            'id', 'title', 'description', 'severity', 'status', 'created_at', 'updated_at',
            # Derived fields from related Event
            'event_id', 'event_type'
        ]
        read_only_fields = ['id', 'title', 'description', 'severity', 'created_at', 'updated_at']


class AlertStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating alert status - Admin only"""
    
    # Status field - validated strictly in validate_status() method
    status = serializers.CharField()
    
    class Meta:
        model = Alert
        fields = ['status']
    
    def validate_status(self, value):
        """Strict validation for status field - rejects invalid enum values"""
        if not value:
            raise serializers.ValidationError('Status is required.')
        
        # Get all valid status choices from model
        valid_statuses = [choice[0] for choice in Alert.STATUS_CHOICES]
        
        # Allowed statuses for updates (subset of valid statuses)
        allowed_statuses = ['ACKNOWLEDGED', 'RESOLVED']
        
        # Normalize input to uppercase for comparison
        value_upper = value.upper() if isinstance(value, str) else value
        
        # First check if it's a valid status choice at all
        if value_upper not in valid_statuses:
            raise serializers.ValidationError(
                f'Status must be one of: {", ".join(valid_statuses)}. Received: "{value}".'
            )
        
        # Then check if it's allowed for updates
        if value_upper not in allowed_statuses:
            raise serializers.ValidationError(
                f'Status can only be changed to: {", ".join(allowed_statuses)}. Received: "{value}".'
            )
        
        # Return normalized value only after all validation passes
        return value_upper
