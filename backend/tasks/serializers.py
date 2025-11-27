from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    """
    class Meta:
        model = Task
        fields = ['id', 'title', 'due_date', 'estimated_hours', 'importance', 
                  'dependencies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskInputSerializer(serializers.Serializer):
    """
    Serializer for task input (no database storage).
    Used for analyze endpoint.
    """
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField(min_value=0.1)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )


class TaskAnalyzeRequestSerializer(serializers.Serializer):
    """
    Serializer for analyze request.
    """
    tasks = TaskInputSerializer(many=True)
    strategy = serializers.ChoiceField(
        choices=['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'],
        default='smart_balance',
        required=False
    )


class SuggestRequestSerializer(serializers.Serializer):
    """
    Serializer for suggest request.
    """
    tasks = TaskInputSerializer(many=True)
    strategy = serializers.ChoiceField(
        choices=['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'],
        default='smart_balance',
        required=False
    )
    count = serializers.IntegerField(min_value=1, max_value=10, default=3, required=False)