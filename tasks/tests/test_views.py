from django.test import TestCase
from app.models import Task
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class CreateTaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='12345')
        self.client.login(username='test_user', password='12345')
        self.url = reverse('create_task')

    def test_task_creation(self):

        resp = self.client.post(self.url, {'name': 'Test Task',
                                                       'description': 'test description',
                                                       'due_date': timezone.now().date(),
                                                       'assignee': self.user,
                                                       'status': 'pending'
                                                       })
        task = Task.objects.get(name='Test Task')
        self.assertEqual(task.name, 'Test Task')


class TaskUpdateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='12345')
        self.other_user = User.objects.create_user(username='other', password='12345')


        self.task = Task.objects.create(
            name='Original Task',
            description='Original description',
            due_date=timezone.now().date(),
            creator=self.user,
            assignee=self.user,
            status='pending'
        )
        self.url = reverse('edit_task', kwargs={'pk': self.task.pk})
        self.today = timezone.now().date()

    def test_update_task(self):
        self.client.logout()
        self.client.login(username='owner', password='12345')
        response = self.client.post(self.url, {
            'name': 'Updated Task',
            'description': 'Updated description',
            'due_date': self.today,
            'assignee': self.user,
            'status': 'done'
        })

        updated_task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'done')


    def test_unauthorized_update(self):
        self.client.logout()
        self.client.login(username='other', password='12345')
        response = self.client.post(self.url, {
            'name': 'Hacked Task',
            'description': 'Hacked description',
            'due_date': self.today,
            'assignee': self.user,
            'status': 'pending'
        })
        self.assertEqual(response.status_code, 403)


class TaskDeleteViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='12345')
        self.other_user = User.objects.create_user(username='other', password='12345')
        self.client.login(username='owner', password='12345')

        self.task = Task.objects.create(
            name='Task to delete',
            description='Delete me',
            due_date=timezone.now().date(),
            creator=self.user,
            assignee=self.user,
            status='pending'
        )
        self.url = reverse('remove_task', kwargs={'pk': self.task.pk})

    def test_delete_task(self):
        response = self.client.post(self.url)
        self.assertEqual(Task.objects.filter(pk=self.task.pk).exists(), False)
        self.assertRedirects(response, reverse('search_tasks'))


class TaskDetailViewTestCase(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', password='12345')
        self.assignee = User.objects.create_user(username='assignee', password='12345')
        self.other_user = User.objects.create_user(username='other', password='12345')

        self.task = Task.objects.create(
            name='Test Task',
            description='Test description',
            due_date=timezone.now().date(),
            creator=self.creator,
            assignee=self.assignee,
            status='pending'
        )

    def test_creator_access(self):
        self.client.login(username='creator', password='12345')
        response = self.client.get(reverse('view_task', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task'], self.task)

    def test_assignee_access(self):
        self.client.login(username='assignee', password='12345')
        response = self.client.get(reverse('view_task', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access(self):
        self.client.login(username='other', password='12345')
        response = self.client.get(reverse('view_task', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 403)


class SearchTasksViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='test_user1', password='12345')
        self.user2 = User.objects.create_user(username='test_user2', password='12345')
        self.user3 = User.objects.create_user(username='test_user3', password='12345')
        self.client.login(username='test_user1', password='12345')

        self.today = timezone.now().date()
        self.yesterday = self.today - timezone.timedelta(days=1)
        self.tomorrow = self.today + timezone.timedelta(days=1)

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

        self.today_iso = self.today.isoformat()
        self.tomorrow_iso = self.tomorrow.isoformat()

    def test_search_without_parameters(self):
        response = self.client.post(reverse('search_tasks'))
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 3)
        self.assertCountEqual(tasks, [self.task1, self.task2, self.task3])

    def test_search_by_keyword(self):
        response = self.client.post(reverse('search_tasks'), {'keywords': 'keyword'})
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task3, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_search_by_creator(self):
        response = self.client.post(reverse('search_tasks'), {'creator': self.user2.id})
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], self.task3)

    def test_search_by_assignee(self):
        response = self.client.post(reverse('search_tasks'), {'assignee': self.user2.id})
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], self.task2)

    def test_search_by_status(self):
        response = self.client.post(reverse('search_tasks'), {'status': 'pending'})
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], self.task1)

    def test_search_by_date_range(self):
        response = self.client.post(reverse('search_tasks'), {
            'start_date': self.today_iso,
            'end_date': self.tomorrow_iso
        })
        tasks = response.context['tasks']
        self.assertEqual(len(tasks), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task2, tasks)
        self.assertNotIn(self.task3, tasks)

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
