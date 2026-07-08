from django.utils import timezone
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import HasResourcePermission, user_has_permission

from .models import Blog
from .serializers import BlogSerializer


class BlogViewSet(viewsets.ModelViewSet):
    """Replaces actions/blogs/*.

    Public (unauthenticated) callers can list/read *published* posts only.
    Managing posts requires the ``blog`` RBAC permission.
    """

    serializer_class = BlogSerializer
    rbac_resource = "blog"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "excerpt"]
    ordering_fields = ["created_at", "published_at", "title"]
    lookup_field = "pk"

    def get_permissions(self):
        if self.action in ("list", "retrieve", "by_slug"):
            return [AllowAny()]
        return [IsAuthenticated(), HasResourcePermission()]

    def _can_manage(self):
        return user_has_permission(self.request.user, "blog", "read")

    def get_queryset(self):
        qs = Blog.objects.select_related("author").all()

        # Non-managers only ever see published posts.
        if not self._can_manage():
            qs = qs.filter(published=True)

        params = self.request.query_params
        if params.get("authorId") and params["authorId"] != "all":
            qs = qs.filter(author_id=params["authorId"])
        published = params.get("published")
        if published and published != "all":
            qs = qs.filter(published=published.lower() == "true")
        if params.get("tags"):
            qs = qs.filter(tags__contains=[params["tags"]])
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        published = serializer.validated_data.get("published")
        published_at = timezone.now() if published else None
        serializer.save(published_at=published_at)

    def perform_update(self, serializer):
        instance = serializer.instance
        published = serializer.validated_data.get("published", instance.published)
        # Stamp published_at the first time a post is published.
        if published and not instance.published_at:
            serializer.save(published_at=timezone.now())
        else:
            serializer.save()

    @action(detail=False, methods=["get"], url_path=r"slug/(?P<slug>[-\w]+)")
    def by_slug(self, request, slug=None):
        """Public fetch by slug for the marketing blog pages."""
        blog = Blog.objects.select_related("author").filter(slug=slug, published=True).first()
        if blog is None:
            return Response({"detail": "Not found."}, status=404)
        return Response(self.get_serializer(blog).data)
