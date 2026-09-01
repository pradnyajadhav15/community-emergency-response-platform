from rest_framework import serializers

from .models import Block, Flat, ResidentProfile, Society


class FlatSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = ["id", "block", "flat_number", "floor", "label"]

    def get_label(self, obj):
        return str(obj)


class BlockSerializer(serializers.ModelSerializer):
    flat_count = serializers.IntegerField(source="flats.count", read_only=True)

    class Meta:
        model = Block
        fields = ["id", "society", "name", "total_floors", "flat_count"]


class SocietySerializer(serializers.ModelSerializer):
    block_count = serializers.IntegerField(source="blocks.count", read_only=True)

    class Meta:
        model = Society
        fields = [
            "id", "name", "code", "address", "city", "state",
            "pincode", "latitude", "longitude", "block_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ResidentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    flat_label = serializers.SerializerMethodField()

    class Meta:
        model = ResidentProfile
        fields = [
            "id", "user", "username", "flat", "flat_label",
            "is_owner", "is_senior_citizen", "notes", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

    def get_flat_label(self, obj):
        return str(obj.flat) if obj.flat else ""
