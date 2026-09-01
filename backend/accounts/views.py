import random

from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import EmergencyContact
from .serializers import (
    CustomTokenObtainPairSerializer,
    EmergencyContactSerializer,
    PushTokenSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def _new_code():
    return f"{random.randint(0, 999999):06d}"


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PushTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PushTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.expo_push_token = serializer.validated_data["expo_push_token"]
        request.user.save(update_fields=["expo_push_token"])
        return Response({"detail": "Push token saved."})


class AvailabilityView(APIView):
    """Volunteers and security toggle whether they can respond."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        value = request.data.get("is_available")
        if not isinstance(value, bool):
            return Response(
                {"detail": "Field 'is_available' must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.is_available = value
        request.user.save(update_fields=["is_available"])
        return Response({"is_available": request.user.is_available})


class DirectoryView(APIView):
    """Contact directory for the user's society."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.society_id:
            return Response([])
        qs = User.objects.filter(
            society_id=request.user.society_id,
            role__in=["SECURITY", "VOLUNTEER", "ADMIN"],
            is_active=True,
        ).exclude(pk=request.user.pk)
        return Response(UserSerializer(qs, many=True).data)


class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmergencyContact.objects.filter(resident=self.request.user)

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user, verification_code=_new_code())

    @action(detail=True, methods=["post"])
    def send_code(self, request, pk=None):
        contact = self.get_object()
        contact.verification_code = _new_code()
        contact.save(update_fields=["verification_code"])
        print(f"[VERIFY] {contact.full_name} {contact.phone} code={contact.verification_code}")
        return Response({"detail": "Verification code sent. Check the server console."})

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        contact = self.get_object()
        code = str(request.data.get("code", "")).strip()
        if code and code == contact.verification_code:
            contact.is_verified = True
            contact.save(update_fields=["is_verified"])
            return Response({"detail": "Contact verified."})
        return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)
