import logging
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Alert
from .serializers import AlertSerializer, AlertStatusUpdateSerializer
from .permissions import AlertPermission

logger = logging.getLogger('alerts')


class AlertViewSet(viewsets.ModelViewSet):
    # Base queryset - get_queryset() will override with optimizations
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [AlertPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']  # Default ordering: newest first

    @extend_schema(
        summary='List alerts',
        description='Retrieve a paginated list of alerts. Supports filtering by status and severity.',
        parameters=[
            OpenApiParameter('status', description='Filter by alert status', required=False, type=str),
            OpenApiParameter('severity', description='Filter by event severity', required=False, type=str),
            OpenApiParameter('ordering', description='Order by field (created_at, status)', required=False, type=str),
        ],
        tags=['Alerts'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optimized queryset with select_related to prevent N+1 queries.
        Efficiently filters by status and severity with proper query optimization.
        
        Query optimizations:
        - select_related('event'): Fetches Event data in a single JOIN query
        - Prevents N+1 queries when accessing event.id and event.event_type in serializer
        - Filtering on event__severity uses the JOIN, avoiding additional queries
        """
        # Use select_related to fetch Event data in a single query
        # This prevents N+1 queries when accessing event.id and event.event_type in serializer
        queryset = Alert.objects.select_related('event').all()
        
        # Safe filter by status - validate against allowed choices
        # Filtering on Alert.status is efficient (direct field access, indexed)
        status_param = self.request.query_params.get('status', None)
        if status_param is not None:
            # Whitelist validation - only allow valid status choices
            valid_statuses = [choice[0] for choice in Alert.STATUS_CHOICES]
            if status_param.upper() in valid_statuses:
                queryset = queryset.filter(status=status_param.upper())
            # Silently ignore invalid status values (security: don't reveal valid choices)
        
        # Safe filter by severity - validate against allowed choices
        # Filtering on event__severity uses the JOIN from select_related, so it's efficient
        # No additional query needed since Event is already joined
        severity_param = self.request.query_params.get('severity', None)
        if severity_param is not None:
            # Import here to avoid circular import
            from events.models import Event
            valid_severities = [choice[0] for choice in Event.SEVERITY_CHOICES]
            if severity_param.upper() in valid_severities:
                # This filter uses the join from select_related, avoiding additional queries
                queryset = queryset.filter(event__severity=severity_param.upper())
            # Silently ignore invalid severity values (security: don't reveal valid choices)
        
        return queryset

    @extend_schema(
        summary='Update alert status',
        description='Update alert status. Admin-only access. Only allows status changes to ACKNOWLEDGED or RESOLVED.',
        request=AlertStatusUpdateSerializer,
        responses={200: AlertStatusUpdateSerializer, 400: AlertStatusUpdateSerializer, 403: None},
        tags=['Alerts'],
    )
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH endpoint to update alert status.
        Admin-only access. Analyst receives 403 Forbidden.
        Only allows status changes to ACKNOWLEDGED or RESOLVED.
        """
        instance = self.get_object()
        old_status = instance.status
        serializer = AlertStatusUpdateSerializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            new_status = instance.status
            logger.info(
                f'Alert status updated: id={instance.id}, '
                f'old_status={old_status}, new_status={new_status}, '
                f'user={request.user.username}'
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.warning(
            f'Alert status update failed: id={instance.id}, '
            f'validation_errors={serializer.errors}, user={request.user.username}'
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)