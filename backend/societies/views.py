from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsSocietyAdminOrReadOnly

from .models import Block, Flat, ResidentProfile, Society
from .serializers import (
    BlockSerializer,
    FlatSerializer,
    ResidentProfileSerializer,
    SocietySerializer,
)


class SocietyViewSet(viewsets.ModelViewSet):
    queryset = Society.objects.all()
    serializer_class = SocietySerializer
    permission_classes = [IsSocietyAdminOrReadOnly]


class BlockViewSet(viewsets.ModelViewSet):
    serializer_class = BlockSerializer
    permission_classes = [IsSocietyAdminOrReadOnly]

    def get_queryset(self):
        qs = Block.objects.select_related("society")
        society = self.request.query_params.get("society")
        return qs.filter(society_id=society) if society else qs


class FlatViewSet(viewsets.ModelViewSet):
    serializer_class = FlatSerializer
    permission_classes = [IsSocietyAdminOrReadOnly]

    def get_queryset(self):
        qs = Flat.objects.select_related("block", "block__society")
        block = self.request.query_params.get("block")
        return qs.filter(block_id=block) if block else qs


class ResidentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ResidentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ResidentProfile.objects.select_related("user", "flat")
        user = self.request.user
        if user.is_staff or user.role == "ADMIN":
            return qs
        return qs.filter(user=user)

    @action(detail=False, methods=["get", "post"], url_path="my-profile")
    def my_profile(self, request):
        profile, _ = ResidentProfile.objects.get_or_create(user=request.user)
        if request.method == "POST":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(self.get_serializer(profile).data)
