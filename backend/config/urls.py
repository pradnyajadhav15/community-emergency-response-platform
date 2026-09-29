from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


def health(request):
    return JsonResponse({
        "service": "CERP - Community Emergency Response Platform API",
        "status": "ok",
        "admin": "/admin/",
        "api": "/api/",
    })


urlpatterns = [
    path("", health, name="health"),
    path("admin/", admin.site.urls),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token-verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("societies.urls")),
    path("api/", include("alerts.urls")),
    path("api/incidents/", include("incidents.urls")),
]