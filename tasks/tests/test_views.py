from django.test import TestCase
from app.models import Task
from django.contrib.auth.models import User
from app.views import (create_task,
                       remove_task,
                       edit_task,
                       search_tasks,
                       view_task
                       )
from django.urls import reverse
from django.utils import timezone


class CreateTaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='12345')
        self.user.save()
        login = self.client.login(username='test_user', password='12345')

    def test_task_creation(self):

        resp = self.client.post(reverse('create_task'), {'name': 'Test Task',
                                                       'description': 'test description',
                                                       'due_date': timezone.now().date(),
                                                       'assignee': self.user,
                                                       'status': 'pending'
                                                       })
        task = Task.objects.get(name='Test Task')
        self.assertEqual(task.name, 'Test Task')
        self.assertRedirects(resp, reverse('home'))


class SearchTasksCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='test_user1', password='12345')
        self.user2 = User.objects.create_user(username='test_user2', password='12345')
        self.user3 = User.objects.create_user(username='test_user3', password='12345')

        self.today = timezone.now().date()
        self.yesterday = self.today - timezone.timedelta(days=1)
        self.tomorrow = self.today + timezone.timedelta(days=1)

        login = self.client.login(username=self.user1, password='12345')

        self.task1 = Task.objects.create(
            name='Important Task',
            description='This is very important task with keyword',
            due_date=self.today,
            creator=self.user1,
            assignee=self.user1,
            status='pending'
        )

        self.task2 = Task.objects.create(
            name='Regular Task',
            description='Normal priority task',
            due_date=self.tomorrow,
            creator=self.user1,
            assignee=self.user2,
            status='done'
        )

        self.task3 = Task.objects.create(
            name='Completed Task',
            description='Task with keyword completed',
            due_date=self.yesterday,
            creator=self.user2,
            assignee=self.user1,
            status='canceled'
        )

    def test_search_without_parameters(self):
        response = self.client.post(reverse('search_tasks'))
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 3)
        self.assertCountEqual(tasks, [self.task1, self.task2, self.task3])


    def test_search_by_keyword(self):
        response = self.client.post(reverse('search_tasks'), {
            'keywords': 'keyword'
        })
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task3, tasks)
        self.assertNotIn(self.task2, tasks)


    def test_search_by_creator(self):
        response = self.client.post(reverse('search_tasks'), {
            'creator': self.user2.id
        })
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], self.task3)


    def test_search_by_assignee(self):
        response = self.client.post(reverse('search_tasks'), {
            'assignee': self.user2.id
        })
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], self.task2)


    def test_search_by_status(self):
        response = self.client.post(reverse('search_tasks'), {
            'status': 'pending'
        })
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], self.task1)


    def test_search_by_date_range(self):
        response = self.client.post(reverse('search_tasks'), {
            'start_date': self.today,
            'end_date': self.tomorrow
        })
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0], self.task1)
        self.assertEqual(tasks[1], self.task2)


    def test_search_combined_filters(self):
        response = self.client.post(reverse('search_tasks'), {
            'keywords': 'task',
            'status': 'done',
            'assignee': self.user2.id
        })
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], self.task2)


    def test_search_only_related_tasks(self):
        unrelated_task = Task.objects.create(
            name='Unrelated Task',
            description='Task not related to user1',
            due_date=timezone.now().date(),
            creator=self.user3,
            assignee=self.user3,
            status='pending'
        )

        response = self.client.post(reverse('search_tasks'))
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 3)
        self.assertNotIn(unrelated_task, tasks)


    def test_search_creator_or_assignee(self):
        response = self.client.post(reverse('search_tasks'), {
            'creator': self.user1.id,
            'assignee': self.user1.id
        })
        tasks = response.context['tasks']

        self.assertEqual(len(tasks), 3)
        self.assertCountEqual(tasks, [self.task1, self.task2, self.task3])

    def test_view_task(self):
        response = self.client.get(reverse('view_task', kwargs={'pk': self.task1.pk}))
        self.assertEqual(response.status_code, 200)
        task = response.context['task']
        self.assertEqual(task.description, self.task1.description)
