from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Task(models.Model):
    """
    Task model representing a single task with priority scoring attributes.
    """
    title = models.CharField(max_length=255)
    due_date = models.DateField()
    estimated_hours = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Estimated hours to complete the task"
    )
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="User-provided importance rating (1-10)"
    )
    dependencies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task IDs that this task depends on"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title