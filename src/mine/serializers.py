from rest_framework.serializers import (
    BooleanField,
    ModelSerializer,
    PrimaryKeyRelatedField,
)

from .models import (
    Command,
    Platform,
    Script,
    Commander,
    Room,
    Worker,
    Job,
)


class CommandSerializer(ModelSerializer):
    class Meta:
        model = Command
        fields = '__all__'


class PlatformSerializer(ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'


class ScriptSerializer(ModelSerializer):
    class Meta:
        model = Script
        fields = '__all__'


class CommanderSerializer(ModelSerializer):
    workers = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Commander
        fields = '__all__'


class RoomSerializer(ModelSerializer):
    workers = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Room
        fields = '__all__'


class WorkerSerializer(ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'


class JobSerializer(ModelSerializer):
    command = PrimaryKeyRelatedField(queryset=Command.objects.all(), write_only=True)
    workers = PrimaryKeyRelatedField(queryset=Worker.objects.all(), many=True, write_only=True)
    force = BooleanField(default=False, write_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = [
            'commander',
            'script',
            'status',
            'submitted_at',
            'started_at',
            'finished_at',
            'returncode',
            'stdout',
            'stderr',
        ]

    def create(self, validated_data):
        # Remove write-only fields
        for k in ['command', 'workers', 'force']:
            validated_data.pop(k, None)
        return super(JobSerializer, self).create(validated_data)
