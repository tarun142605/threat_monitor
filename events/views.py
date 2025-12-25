import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Event
from .serializers import EventSerializer
from .permissions import EventPermission

logger = logging.getLogger('events')


class EventIngestionThrottle(UserRateThrottle):
    """Custom throttle for event ingestion endpoint"""
    rate = '100/minute'


@extend_schema(
    summary='Create a new security event',
    description='Ingest a new security event. Admin-only access. Rate limited to 100 requests per minute.',
    request=EventSerializer,
    responses={201: EventSerializer, 400: EventSerializer, 403: None},
    tags=['Events'],
)
@api_view(['POST'])
@permission_classes([EventPermission])
@throttle_classes([EventIngestionThrottle])
def create_event(request):
    """
    POST endpoint to create a new event.
    Admin-only access. Analyst receives 403 Forbidden.
    Rate limited to 100 requests per minute.
    """
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid(raise_exception=False):
        event = serializer.save()
        logger.info(
            f'Event ingested: id={event.id}, type={event.event_type}, '
            f'severity={event.severity}, source={event.source_name}, '
            f'user={request.user.username}'
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    logger.warning(
        f'Event ingestion failed: validation_errors={serializer.errors}, '
        f'user={request.user.username}'
    )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)