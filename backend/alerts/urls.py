from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .stats import DashboardStatsView
from .views import MyNotificationViewSet, SOSAlertViewSet

router = DefaultRouter()
router.register("sos", SOSAlertViewSet, basename="sos")
router.register("notifications", MyNotificationViewSet, basename="notification")

urlpatterns = [
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("", include(router.urls)),
]
