from django.urls import path

from .views import (
    PhoneNumberView,
)

urlpatterns = [
    path('id2pn', PhoneNumberView.as_view(), name='id2pn'),
]
