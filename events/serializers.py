from rest_framework import serializers
from django.utils.html import strip_tags
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    severity = serializers.ChoiceField(
        choices=Event.SEVERITY_CHOICES,
        error_messages={
            'invalid_choice': 'Severity must be one of: LOW, MEDIUM, HIGH, CRITICAL'
        }
    )
    source_name = serializers.CharField(max_length=200, min_length=1, trim_whitespace=True)
    event_type = serializers.CharField(max_length=200, min_length=1, trim_whitespace=True)
    description = serializers.CharField(min_length=1, trim_whitespace=True)

    class Meta:
        model = Event
        fields = ['id', 'source_name', 'event_type', 'severity', 'description', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def validate_severity(self, value):
        """Strict validation for severity field"""
        if not value:
            raise serializers.ValidationError('Severity is required.')
        valid_severities = [choice[0] for choice in Event.SEVERITY_CHOICES]
        if value not in valid_severities:
            raise serializers.ValidationError(
                f'Severity must be one of: {", ".join(valid_severities)}'
            )
        return value.upper()  # Normalize to uppercase

    def validate_source_name(self, value):
        """Validate and sanitize source_name"""
        if not value or not value.strip():
            raise serializers.ValidationError('Source name cannot be empty.')
        # Remove HTML tags to prevent XSS
        cleaned = strip_tags(value.strip())
        if len(cleaned) > 200:
            raise serializers.ValidationError('Source name cannot exceed 200 characters.')
        return cleaned

    def validate_event_type(self, value):
        """Validate and sanitize event_type"""
        if not value or not value.strip():
            raise serializers.ValidationError('Event type cannot be empty.')
        # Remove HTML tags to prevent XSS
        cleaned = strip_tags(value.strip())
        if len(cleaned) > 200:
            raise serializers.ValidationError('Event type cannot exceed 200 characters.')
        return cleaned

    def validate_description(self, value):
        """Validate and sanitize description"""
        if not value or not value.strip():
            raise serializers.ValidationError('Description cannot be empty.')
        # Remove HTML tags to prevent XSS
        cleaned = strip_tags(value.strip())
        return cleaned

    def validate(self, attrs):
        """Cross-field validation"""
        # Ensure all required fields are present
        required_fields = ['source_name', 'event_type', 'severity', 'description']
        for field in required_fields:
            if field not in attrs or not attrs[field]:
                raise serializers.ValidationError({field: f'{field} is required.'})
        return attrs
