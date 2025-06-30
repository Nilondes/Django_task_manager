from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Task(models.Model):
    statuses = (
        ("pending", "pending"),
        ("done", "done"),
        ("canceled", "canceled")
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    creator = models.ForeignKey(User, to_field='username', on_delete=models.CASCADE, related_name='created_tasks')
    assignee = models.ForeignKey(User, to_field='username', on_delete=models.CASCADE, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=statuses)

    def clean(self):
        if self.due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past")

    def __str__(self):
        return f'{self.name} | Creator: {self.creator} | Assignee: {self.assignee} | Due: {self.due_date}'
