from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from .forms import RegistrationForm, TaskForm, SearchTaskForm
from .models import Task
from django.db.models import Q
from functools import reduce
import operator


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'registration/login.html', {'error_message': 'Invalid login'})
    else:
        return render(request, 'registration/login.html')


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
    return render(request, 'home.html')


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('search_tasks')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('search_tasks')

    def test_func(self):
        task = self.get_object()
        return task.creator == self.request.user


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('search_tasks')
    template_name = 'tasks/search_tasks.html'

    def test_func(self):
        task = self.get_object()
        return task.creator == self.request.user


class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/view_task.html'
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        return task.creator == self.request.user or task.assignee == self.request.user


@login_required
def search_tasks(request):
    if request.method == 'POST':
        form = SearchTaskForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            creator = form.cleaned_data['creator']
            assignee = form.cleaned_data['assignee']
            status = form.cleaned_data['status']
            keywords = form.cleaned_data['keywords'].split() if form.cleaned_data['keywords'] else []

            base_query = Q(creator=request.user) | Q(assignee=request.user)
            tasks = Task.objects.filter(base_query)

            if start_date:
                tasks = tasks.filter(due_date__gte=start_date)

            if end_date:
                tasks = tasks.filter(due_date__lte=end_date)

            if status:
                tasks = tasks.filter(status=status)

            if keywords:
                keyword_q = reduce(operator.or_,
                                  (Q(name__icontains=keyword) | Q(description__icontains=keyword)
                                   for keyword in keywords
                                    )
                                   )
                tasks = tasks.filter(keyword_q)

            creator_assignee_q = Q()
            if creator:
                creator_assignee_q |= Q(creator=creator)
            if assignee:
                creator_assignee_q |= Q(assignee=assignee)

            if creator or assignee:
                tasks = tasks.filter(creator_assignee_q)

            context = {'tasks': tasks, 'form': form}
            return render(request, 'tasks/search_tasks.html', context)
    else:
        form = SearchTaskForm()
    return render(request, 'tasks/search_tasks.html', {'form': form})
