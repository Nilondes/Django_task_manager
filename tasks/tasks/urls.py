"""
URL configuration for tasks project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app.views import (register,
                       user_login,
                       home,
                       create_task,
                       user_logout,
                       remove_task,
                       edit_task,
                       search_tasks,
                       view_task,
                       )


urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('create_task/', create_task, name='create_task'),
    path('edit_task/<int:pk>', edit_task, name='edit_task'),
    path('remove_task/<int:pk>', remove_task, name='remove_task'),
    path('search_tasks/', search_tasks, name='search_tasks'),
    path('search_tasks/<int:pk>', view_task, name='view_task'),
    path('admin/', admin.site.urls),
]
