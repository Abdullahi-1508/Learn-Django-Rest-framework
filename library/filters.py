# library/filters.py
import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    # Simple fields: filter by exact match
    author = django_filters.NumberFilter(field_name='author__id')
    published_year = django_filters.NumberFilter(field_name='published_year')
    title = django_filters.CharFilter(lookup_expr='icontains')   # case-insensitive contains

    # Ranges: ?published_year_min=1950&published_year_max=2000
    published_year_min = django_filters.NumberFilter(
        field_name='published_year', lookup_expr='gte'
    )
    published_year_max = django_filters.NumberFilter(
        field_name='published_year', lookup_expr='lte'
    )

    class Meta:
        model = Book
        fields = []   # we use explicit fields above