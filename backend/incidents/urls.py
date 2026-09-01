from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IncidentMessageViewSet, ResponderAssignmentViewSet

router = DefaultRouter()
router.register("messages", IncidentMessageViewSet, basename="incident-message")
router.register("assignments", ResponderAssignmentViewSet, basename="assignment")

urlpatterns = [path("", include(router.urls))]
