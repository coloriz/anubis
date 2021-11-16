from django.contrib.admin import ModelAdmin, register

from .models import (
    PhoneNumberRequestLog,
)


@register(PhoneNumberRequestLog)
class PhoneNumberRequestLogAdmin(ModelAdmin):
    pass
