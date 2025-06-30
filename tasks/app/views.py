import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, TaskForm, SearchTaskForm
from .models import Task
from django.contrib.auth.models import User
from django.db.models import Q
from functools import reduce
import operator
from django.utils import timezone


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


def user_logout(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        logout(request)
    return render(request, 'home.html')


def create_task(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.creator = request.user
            task.save()
            return redirect('home')
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})


def remove_task(request, pk):
    if not request.user.is_authenticated:
        return redirect('home')
    task = Task.objects.get(pk=pk)
    if task.creator != request.user:
        return redirect('home')
    task.delete()
    return redirect('user_tasks')


def edit_task(request, pk):
    if not request.user.is_authenticated:
        return redirect('home')
    task = Task.objects.get(pk=pk)
    if task.creator != request.user:
        return redirect('home')
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('user_tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, 'ads/create_task.html', {'form': form})


def search_tasks(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SearchTaskForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date'] or timezone.now().date()
            end_date = form.cleaned_data['end_date'] or datetime.date.max
            creator = form.cleaned_data['creator']
            assignee = form.cleaned_data['assignee']
            status = form.cleaned_data['status']
            keywords = form.cleaned_data['keywords'].split() if form.cleaned_data['keywords'] else []

            base_query = Q(creator=request.user) | Q(assignee=request.user)
            tasks = Task.objects.filter(base_query)

            tasks = tasks.filter(
                due_date__gte=start_date,
                due_date__lte=end_date
            )

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


def view_task(request, pk):
    if not request.user.is_authenticated:
        return redirect('home')
    task = Task.objects.get(pk=pk)
    if task.creator != request.user or task.assignee != request.user:
        return redirect('home')
    context = {'task': task}
    return render(request, 'tasks/view_task.html', context)
