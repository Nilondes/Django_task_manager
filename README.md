# Django_task_manager

This is a Django app that allows to add, edit, view and remove tasks. 

The service also allows viewing tasks by specified filters (date, status, creator, assignee, keywords).

Users can manage their own tasks and assign tasks to others.

## Stack

- **Backend**: Django 5.2
- **Database**: PostgreSQL 14
- **Containerization**: Docker + Docker Compose
- **Frontend**: HTML + Bootstrap

## Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- PostgreSQL client


## Getting started

```sh
   git clone https://github.com/your-username/task-management-system.git
   cd task-management-system
```

The main directory should contain .env file:

PG_USER=username

PG_PASSWORD=password

PG_DATABASE=database

To start Docker from main directory:

```sh
$ docker compose up --build

```

It will be available at http://localhost:8000

To run tests:

```sh
$ python /tasks/manage.py tests

```