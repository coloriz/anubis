from rest_framework import status
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import (
    GenericViewSet,
    ReadOnlyModelViewSet,
)
from rest_framework_api_key.permissions import HasAPIKey

from .exceptions import JobCancellationFailed
from .executors import JobExecutor
from .models import (
    Command,
    Platform,
    Script,
    Commander,
    Room,
    Worker,
    Job,
)
from .pagination import StandardResultsSetPagination
from .serializers import (
    CommandSerializer,
    PlatformSerializer,
    ScriptSerializer,
    CommanderSerializer,
    RoomSerializer,
    WorkerSerializer,
    JobSerializer,
)


class CommandViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser | HasAPIKey]
    queryset = Command.objects.all()
    serializer_class = CommandSerializer


class PlatformViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser | HasAPIKey]
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


class ScriptViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser | HasAPIKey]
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer


class CommanderViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser | HasAPIKey]
    queryset = Commander.objects.all()
    serializer_class = CommanderSerializer


class RoomViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser | HasAPIKey]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class WorkerViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser | HasAPIKey]
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    filterset_fields = ['enabled', 'room', 'notification']


class JobViewSet(ListModelMixin,
                 RetrieveModelMixin,
                 GenericViewSet):
    permission_classes = [IsAdminUser | HasAPIKey]
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    pagination_class = StandardResultsSetPagination

    _executor = JobExecutor()

    def create(self, request: Request, *args, **kwargs):
        """
        Deserialize request `Job` object,
        create job and put it in the queue of executor.
        """
        # TODO: Use post_save signal to submit created job
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        command = data['command']
        workers = data['workers']

        # Check if all workers have the same commander
        commanders = set(map(lambda x: x.commander, workers))
        if len(commanders) > 1:
            raise ValidationError('All workers must have the same commander')

        # Check if commander supports this command
        commander = commanders.pop()
        if command not in commander.supported_commands.all():
            raise ValidationError(f"Commander does not support '{command.pk}' command")

        # Build script
        script = Script.objects.get(command=command, platform=commander.platform)
        formatted_script = eval(script.body, data)

        # Create job and submit
        job = serializer.save(commander=commander, script=formatted_script, **data)
        self._executor.submit(job)

        headers = {
            'Location': reverse('job-detail', [job.pk], request=request),
        }
        return Response(status=status.HTTP_202_ACCEPTED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        """Cancel the job"""
        job = self.get_object()
        cancelled = self._executor.cancel(job)
        if not cancelled:
            raise JobCancellationFailed
        # Update instnace to cancelled state
        job.refresh_from_db()
        serializer = self.get_serializer(job)
        return Response(serializer.data)
