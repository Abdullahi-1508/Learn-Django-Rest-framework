from rest_framework import serializers
from .models import Book, Author
# For date Validation
from datetime import date
# For Auth
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password



class AuthorSerializer(serializers.ModelSerializer):
    # Nested Serializer
    books = serializers.SerializerMethodField()
    class Meta:
        model = Author
        fields = ['id', 'name', 'country', "books"]
        read_only_fields = ['id']

    def get_books(self, author):
        books = getattr(author, 'recent_books', author.books.all())
        return [
            {'id': b.id, 'title': b.title, 'published_year': b.published_year}
            for b in books
        ]


class AuthorLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'country']


class BookSerializer(serializers.ModelSerializer):
    # Nested Serializer
    author = AuthorLiteSerializer(read_only=True) # For Read
    # To create or Update
    author_id = serializers.PrimaryKeyRelatedField(
        queryset= Author.objects.all(),
        source= "author",
        write_only= True
    )
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author','author_id', 'published_year',
            "cover", 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
        validators = []

    def validate_published_year(self, value):
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Published year cannot be in the future (current year: {current_year})."
            )
        return value

    def validate(self, attrs):
        title = attrs.get('title') or getattr(self.instance, 'title', None)
        author = attrs.get('author') or getattr(self.instance, 'author', None)
        qs = Book.objects.filter(title=title, author=author)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "This author already has a book with this title."
            )
        return attrs

    def validate_cover(self, value):
        """Validate file size and image integrity."""
        if value is None:
            return value
        
        # Size limit: 5 MB
        MAX_SIZE = 5 * 1024 * 1024
        if value.size > MAX_SIZE:
            raise serializers.ValidationError(
                f"Cover image must be 5 MB or smaller. Got {value.size / (1024 * 1024):.1f} MB."
            )
        
        # ImageField already validates that the file is a real image (via Pillow).
        # But you can add extra checks here if needed:
        # - Allowed extensions: .jpg, .png, .webp
        # - Reject SVG (can contain scripts)
        
        return value
# For ViewSet You do not need create because it has already generated but its compulsory in APIView 
"""
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return Book.objects.create(**validated_data)

    def update(self, instance, validated_data):
        old_title = instance.title
        instance = super().update(instance, validated_data)
        if old_title != instance.title:
            print(f"[AUDIT] Book {instance.id} title changed: '{old_title}' to '{instance.title}'")
        return instance
"""


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only= True, validators= [validate_password])

    class Meta:
        model = User
        fields = ["username", "email","password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email= validated_data.get("email", ""),
            password=validated_data["password"],
        )