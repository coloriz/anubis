from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CommandViewSet,
    PlatformViewSet,
    ScriptViewSet,
    CommanderViewSet,
    RoomViewSet,
    WorkerViewSet,
    JobViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'commands', CommandViewSet)
router.register(r'platforms', PlatformViewSet)
router.register(r'scripts', ScriptViewSet)
router.register(r'commanders', CommanderViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'workers', WorkerViewSet)
router.register(r'jobs', JobViewSet)

urlpatterns = [
    path('', include(router.urls))
]
