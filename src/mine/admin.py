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
    pass


@register(Platform)
class PlatformAdmin(ModelAdmin):
    pass


@register(Script)
class ScriptAdmin(ModelAdmin):
    pass


@register(Commander)
class CommanderAdmin(ModelAdmin):
    pass


@register(Room)
class RoomAdmin(ModelAdmin):
    pass


@register(Worker)
class WorkerAdmin(ModelAdmin):
    pass


@register(Job)
class JobAdmin(ModelAdmin):
    pass
