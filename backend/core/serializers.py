from rest_framework import serializers

from .models import ApiKey, ContactSubmission, Organization, OrganizationMember, Setting


class ApiKeySerializer(serializers.ModelSerializer):
    keyPrefix = serializers.CharField(source="key_prefix", read_only=True)
    lastUsedAt = serializers.DateTimeField(source="last_used_at", read_only=True)
    expiresAt = serializers.DateTimeField(source="expires_at", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = ApiKey
        fields = ("id", "name", "keyPrefix", "lastUsedAt", "expiresAt", "createdAt")


class OrganizationSerializer(serializers.ModelSerializer):
    ownerId = serializers.PrimaryKeyRelatedField(source="owner", read_only=True)
    memberCount = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Organization
        fields = (
            "id", "name", "slug", "description", "logo", "ownerId",
            "memberCount", "role", "createdAt", "updatedAt",
        )
        read_only_fields = ("id", "ownerId", "slug")

    def get_memberCount(self, obj):
        return obj.members.count()

    def get_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        member = obj.members.filter(user=request.user).first()
        return member.role if member else ("owner" if obj.owner_id == request.user.id else None)


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    joinedAt = serializers.DateTimeField(source="joined_at", read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ("id", "role", "user", "joinedAt")

    def get_user(self, obj):
        return {
            "id": str(obj.user.id),
            "name": obj.user.name,
            "email": obj.user.email,
            "image": obj.user.image,
        }


class SettingSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Setting
        fields = ("id", "key", "value", "type", "createdAt", "updatedAt")
        read_only_fields = ("id",)


class ContactSubmissionSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name", min_length=2)
    phoneNumber = serializers.CharField(
        source="phone_number", required=False, allow_blank=True, allow_null=True
    )
    message = serializers.CharField(min_length=10)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = ContactSubmission
        fields = (
            "id",
            "fullName",
            "email",
            "phoneNumber",
            "message",
            "status",
            "createdAt",
        )
        read_only_fields = ("id", "status", "createdAt")
