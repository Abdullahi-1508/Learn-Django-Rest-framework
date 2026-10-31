from django.urls import path
from . import views
# For ViewSet
from rest_framework.routers import DefaultRouter
# For Rate limiting
from rest_framework_simplejwt.views import TokenObtainPairView
from .throttles import LoginRateThrottle
# For Class APIView
"""
urlpatterns = [
    path("test/authors", views.AuthorAPIView.as_view()),
    path("test/books", views.BookAPIView.as_view()),
    path("test/books/<int:pk>", views.BookAPIView.as_view()),
    path('register', views.RegisterAPIView.as_view()),
]
"""

# For ViewSet
router = DefaultRouter()
router.register(r"books", views.BookViewSet, basename="book")
router.register(r"authors", views.AuthorViewSet, basename="author")

class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]

urlpatterns = router.urls + [
    path('api/token/', ThrottledTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("register/", views.RegisterAPIView.as_view(), name= "register"),
    ]
# Media and files url are in projects urls