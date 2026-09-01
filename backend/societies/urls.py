from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BlockViewSet, FlatViewSet, ResidentProfileViewSet, SocietyViewSet

router = DefaultRouter()
router.register("societies", SocietyViewSet, basename="society")
router.register("blocks", BlockViewSet, basename="block")
router.register("flats", FlatViewSet, basename="flat")
router.register("residents", ResidentProfileViewSet, basename="resident")

urlpatterns = [path("", include(router.urls))]
