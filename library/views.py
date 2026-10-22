from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer, RegisterSerializer
# For Auth
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
# For Permission
from .permissions import IsOwnerOrReadOnly
# For view Set
from rest_framework import viewsets
from rest_framework.decorators import action
# For Filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BookFilter
# For Search, ordering
from rest_framework.filters import SearchFilter,OrderingFilter
# For pagination
from .pagination import StandardPagination
# For N+1
from django.db.models import Prefetch
# For ratelimiting
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle

#Class APIView
"""
class AuthorAPIView(APIView):
    permission_classes= [IsAuthenticatedOrReadOnly]
    def get(self, request):
        authors = Author.objects.prefetch_related('books').all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
class BookAPIView(APIView):
    permission_classes= [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get(self, request):
        data = Book.objects.all()
        serializer = BookSerializer(data, many=True)
        return(Response(serializer.data))

    def get(self, request, pk):
            data = get_object_or_404(Book, id=pk)
            serializer = BookSerializer(data)
            return(Response(serializer.data))

    def post(self, request):
        serializer = BookSerializer(data=request.data,
                                    context= {"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        self.check_object_permissions(request, book) # This will check the permission
        serializer = BookSerializer(
            instance=book,
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        self.check_object_permissions(request, book) # This will check the permission
        serializer = BookSerializer(
            instance=book,
            data=request.data,
            partial=True,     #  the key difference from put()
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        self.check_object_permissions(request, book) # This will check the permission
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""
# Registration View
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():             
            user = serializer.save()           
            return Response(
                {'id': user.id, 'username': user.username},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View Set

class BookViewSet(viewsets.ModelViewSet):
    # For N+1
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # For Filters, Searching, Ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter

    search_fields = ['title', 'author__name']

    ordering_fields = ['published_year', 'title']
    ordering = ["-created_at", "-id"]

    pagination_class = StandardPagination
    # for rate limiting
    # Default will do the work
    #throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def perform_create(self, serializer):
        # attach current user to create
        if self.request.user.is_authenticated:
            serializer.save(created_by= self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=["get"])
    def recent(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        books = queryset.order_by('-published_year')[:5]
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)    

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.prefetch_related(
        Prefetch(
            'books',
            queryset=Book.objects.order_by('-published_year')[:3],   # top 3 per author
            to_attr='recent_books',   # store as author.recent_books
        )
    ).all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = ['name', 'country']
    ordering = ['name']
    pagination_class = StandardPagination
     # for rate limiting
    # Default will do the work
    #throttle_classes = [AnonRateThrottle, UserRateThrottle]