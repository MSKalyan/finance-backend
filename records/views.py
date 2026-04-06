from rest_framework import viewsets

from core.throttles import RecordThrottle
from finance_backend import settings
from .models import Record
from .serializers import RecordSerializer
from users.permissions import RecordPermission
from django.db import models
from core.pagination import StandardResultsSetPagination 
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [RecordPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    throttle_classes = [RecordThrottle]    
    filterset_fields = {
        'type': ['exact'],              # income / expense
        'category': ['exact', 'icontains'],
        'date': ['exact', 'gte', 'lte'],
        'amount': ['gte', 'lte'],
    }

    # Search (keyword-based)
    search_fields = [
        'category',
        'custom_category',
        'description',
    ]

    # Ordering (sorting)
    ordering_fields = ['date', 'amount']
    ordering = ['-date']  # default
    def get_queryset(self):
        queryset = super().get_queryset()  # 🔥 shared data model

        category = self.request.query_params.get('category')
        category=category.lower().strip() if category else None
        if category:
            queryset = queryset.filter(
                models.Q(category__iexact=category) |
                models.Q(custom_category__iexact=category)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Record soft deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )