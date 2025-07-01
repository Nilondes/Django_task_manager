from django.test import TestCase
from app.models import Task
from django.contrib.auth.models import User
from django.utils import timezone


class CreateTask(TestCase):
    def test_task_creation(self):
        user = User.objects.create_user(username='test user')
        task = Task.objects.create(name='Test Task',
                               description='test_description',
                               due_date=timezone.now().date(),
                               creator=user,
                               assignee=user,
                               status='pending'
                               )
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.description, 'test_description')
        self.assertEqual(task.status, 'pending')
