from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token-verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("societies.urls")),
    path("api/", include("alerts.urls")),
    path("api/incidents/", include("incidents.urls")),
]
