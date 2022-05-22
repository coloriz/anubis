from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.models import (
    Model,
    TextChoices,
    UniqueConstraint,
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    IntegerField,
    TextField,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Command(Model):
    id = CharField(max_length=16, primary_key=True)

    def __str__(self):
        return f'{self.id}'


class Platform(Model):
    id = CharField(max_length=16, primary_key=True)

    def __str__(self):
        return f'{self.id}'


class Script(Model):
    command = ForeignKey(Command, on_delete=CASCADE, related_name='scripts')
    platform = ForeignKey(Platform, on_delete=CASCADE, related_name='scripts')
    body = TextField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['command', 'platform'], name='unique_command_platform'),
        ]

    def __str__(self):
        return f'{self.__class__.__name__} object ({self.pk}, {self.command}, {self.platform})'


class Commander(Model):
    id = CharField(max_length=32, primary_key=True)
    platform = ForeignKey(Platform, on_delete=CASCADE, related_name='commanders')
    args_fmt = CharField(max_length=255, default='ssh -T {id} {script}')
    supported_commands = ManyToManyField(Command, related_name='commanders')

    def __str__(self):
        return f'{self.id}'


class Room(Model):
    id = CharField(max_length=6, primary_key=True)
    ac_address = CharField(max_length=8)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.id}'


class Worker(Model):
    id = CharField(max_length=32, primary_key=True)
    enabled = BooleanField(default=False)
    mac_address = CharField(max_length=17, validators=[RegexValidator(r'^([0-9A-F]{2}-){5}([0-9A-F]{2})$')])
    room = ForeignKey(Room, on_delete=CASCADE, related_name='workers', null=True)
    commander = ForeignKey(Commander, on_delete=CASCADE, related_name='workers')
    notification = BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.id}'


class Job(Model):
    class Status(TextChoices):
        QUEUED = 'QUEUED', _('Queued')
        RUNNING = 'RUNNING', _('Running')
        DONE = 'DONE', _('Done')
        TIMEOUT = 'TIMEOUT', _('Timeout')
        CANCELLED = 'CANCELLED', _('Cancelled')

    commander = ForeignKey(Commander, on_delete=CASCADE, related_name='jobs')
    script = TextField()
    timeout = IntegerField(default=600, validators=[MinValueValidator(0), MaxValueValidator(86400)])
    status = CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    submitted_at = DateTimeField(db_index=True, default=timezone.now)
    started_at = DateTimeField(blank=True, null=True)
    finished_at = DateTimeField(blank=True, null=True)
    returncode = IntegerField(blank=True, null=True)
    stdout = TextField(blank=True, null=True)
    stderr = TextField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']

    def set_state_running(self):
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()

    def set_state_done(self, returncode: int, stdout: str, stderr: str):
        self.status = self.Status.DONE
        self.finished_at = timezone.now()
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def set_state_timeout(self):
        self.status = self.Status.TIMEOUT
        self.finished_at = timezone.now()

    def set_state_cancelled(self):
        self.status = self.Status.CANCELLED
        self.finished_at = timezone.now()
