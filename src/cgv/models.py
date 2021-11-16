from django.core.validators import RegexValidator
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    GenericIPAddressField,
    TextField,
)
from django.utils import timezone


class PhoneNumberRequestLog(Model):
    at = DateTimeField(db_index=True, default=timezone.now)
    ip = GenericIPAddressField()
    user_id = CharField(max_length=16, validators=[RegexValidator(r'^[a-z0-9]{6,12}$')])
    phone_number = CharField(max_length=16, blank=True)
    status_code = CharField(max_length=3, blank=True)
    raw_response = TextField(blank=True)
    error_msg = CharField(max_length=64, blank=True)

    def __str__(self):
        return f'{self.at.replace(microsecond=0).isoformat()} {self.ip} {self.user_id} {self.phone_number}'
