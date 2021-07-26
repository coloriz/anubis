from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class JobCancellationFailed(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('Failed to cancel job.')
    default_code = 'job_cancellation_failed'
