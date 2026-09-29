from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminUserViewSet,
    AvailabilityView,
    DirectoryView,
    EmergencyContactViewSet,
    LoginView,
    MeView,
    PushTokenView,
    RegisterView,
)

router = DefaultRouter()
router.register("emergency-contacts", EmergencyContactViewSet, basename="emergency-contact")
router.register("users", AdminUserViewSet, basename="admin-user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("push-token/", PushTokenView.as_view(), name="push-token"),
    path("availability/", AvailabilityView.as_view(), name="availability"),
    path("directory/", DirectoryView.as_view(), name="directory"),
    path("", include(router.urls)),
]