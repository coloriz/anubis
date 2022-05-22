from django.contrib.admin import ModelAdmin, register

from .models import (
    Command,
    Platform,
    Script,
    Commander,
    Room,
    Worker,
    Job,
)


@register(Command)
class CommandAdmin(ModelAdmin):
    list_display = ('id',)


@register(Platform)
class PlatformAdmin(ModelAdmin):
    list_display = ('id',)


@register(Script)
class ScriptAdmin(ModelAdmin):
    list_display = ('id', 'command', 'platform')


@register(Commander)
class CommanderAdmin(ModelAdmin):
    list_display = ('id', 'platform')


@register(Room)
class RoomAdmin(ModelAdmin):
    list_display = ('id', 'ac_address')


@register(Worker)
class WorkerAdmin(ModelAdmin):
    list_display = (
        'id',
        'enabled',
        'mac_address',
        'room',
        'commander',
        'notification',
    )
    list_filter = (
        'enabled',
        'room',
        'commander',
        'notification',
    )


@register(Job)
class JobAdmin(ModelAdmin):
    pass
