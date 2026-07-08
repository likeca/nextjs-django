from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Blog


class BlogAuthorSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class BlogSerializer(serializers.ModelSerializer):
    coverImage = serializers.CharField(source="cover_image", required=False, allow_null=True, allow_blank=True)
    publishedAt = serializers.DateTimeField(source="published_at", required=False, allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    authorId = serializers.PrimaryKeyRelatedField(source="author", read_only=True)
    author = BlogAuthorSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = (
            "id",
            "title",
            "slug",
            "content",
            "excerpt",
            "coverImage",
            "authorId",
            "author",
            "published",
            "publishedAt",
            "tags",
            "createdAt",
            "updatedAt",
        )
        read_only_fields = ("id", "author", "authorId")

    def create(self, validated_data):
        # author comes from the request user (set in the view)
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
