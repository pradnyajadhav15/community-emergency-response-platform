from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import EmergencyContact

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "role_display", "phone", "is_phone_verified",
            "is_available", "is_staff", "date_joined",
        ]
        read_only_fields = ["id", "role", "is_phone_verified", "is_staff", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "password2",
            "first_name", "last_name", "role", "phone",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class PushTokenSerializer(serializers.Serializer):
    expo_push_token = serializers.CharField(max_length=255)


class EmergencyContactSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(
        source="get_escalation_level_display", read_only=True
    )

    class Meta:
        model = EmergencyContact
        fields = [
            "id", "full_name", "phone", "email", "relationship",
            "escalation_level", "level_display", "order",
            "is_verified", "linked_user", "created_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        level = attrs.get("escalation_level", getattr(self.instance, "escalation_level", 1))
        order = attrs.get("order", getattr(self.instance, "order", 1))
        qs = EmergencyContact.objects.filter(
            resident=user, escalation_level=level, order=order
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"order": "A contact already exists at this level and order."}
            )
        return attrs


class AdminUserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    society_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "role_display", "phone", "society", "society_name",
            "is_active", "is_available", "is_staff", "date_joined", "last_login",
        ]
        read_only_fields = ["id", "username", "is_staff", "date_joined", "last_login"]

    def get_society_name(self, obj):
        return obj.society.name if obj.society else ""