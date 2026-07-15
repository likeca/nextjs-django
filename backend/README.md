# UV

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
wget -qO- https://astral.sh/uv/install.sh | sh

# Install requirments
uv sync

# Github Action
sudo ln -s /home/ubuntu/.local/bin/uv /usr/local/bin/uv
```

## Async views

- For the function-based view, declaring the whole view using "async def"
- For the class-based view, declaring the HTTP method handlers, such as "async def get()" and "async def post()"

## Queries & the ORM

```bash
async for author in Author.objects.filter(name__startswith="A"):
   book = await author.books.afirst()
```

## Features

- Ready Bootstrap-themed pages
- User Registration/Sign up
- Better Security with [12-Factor](http://12factor.net/) recommendations
- Logging/Debugging Helpers
- Works on Python 3 and Django 2

# {{ project_name }}

!!! project name CAN NOT use '-' due to python conflict

## Installation

1. Change project name and nextjs_django folder name

### Quick start

```bash
# Install all dependencies:
uv sync

# Run migrations: # Update database change scripts
uv run manage.py makemigrations

# Update database change
uv run manage.py migrate

# Create superuser
uv run manage.py createsuperuser

# Production Deployment
daphne myproject.asgi:application
```

# django-allauth Google Authenticate

https://www.youtube.com/watch?v=NG48CLLsb1A
https://developers.google.com/gmail/api/quickstart/js
https://console.developers.google.com/
[PO File Translate](https://pofile.net/free-po-editor)

# Django create app add to project

```bash
(venv)$ uv run manage.py startapp <new_app>
```

# Update Table (Drop Table Method)

## Method 1:

1. Delete application relate tables and data
   $ uv run manage.py migrate registrationform zero
2. Recreate Table
   $ uv run manage.py ./manage.py migrate

## Method 2:

1. Export Data from Workbench (Data Only)
2. Update exported data
3. Drop Table from database
4. Update Drop Table status in Django
   $ uv run manage.py ./manage.py migrate --fake [table_name] zero
5. Recreate Table
   $ uv run manage.py ./manage.py migrate

# Django SEO

The ping_google() command only works if you have registered your site with Google Webmaster Tools.
Registered your site with Google Webmaster Tools.
[Google Search Console](https://www.google.com/webmasters/tools/)

```bash
uv run manage.py ping_google
```

# Daphne

daphne backend.asgi:application

# Django Auto Translate - django-autotranslate

```bash
# Translate language
uv run manage.py makemessages -a
uv run manage.py makemessages -l fr
uv run manage.py makemessages -l zh_Hans

# Compile language po for production
uv run manage.py compilemessages -l fr -l zh_Hans

# django-autotranslate (User custom version)
uv run manage.py translate_messages -u -f
uv run manage.py compilemessages
```

# gettext() vs gettext_lazy()

## Use gettext_lazy() in forms or models

In definitions like forms or models you should use gettext_lazy because the code of this definitions is only executed once (mostly on django's startup);

## use gettext()) in view

In views and similar function calls you can use gettext without problems, because everytime the view is called gettext will be newly executed, so you will always get the right translation fitting the request!

# Provide initial data

uv run manage.py loaddata api/books.json

# Generating an OpenAPI Schema

```bash
uv run manage.py generateschema --file static/site/openapi/schema.yaml
```

# Google Login "Invalid id_token"

django-allauth==0.50.0
dj-rest-auth==4.0.1

# Test SendEmail

```bash
uv run manage.py shell

>>> from dharro.utils import SendEmail
>>> SendEmail('test', 'test')
```

# Squash Migration

```bash
# Apply all change to DB
uv run manage.py migrate

# Squash merge from 0003_faqcategory_order (last migration) to 0002_faqcategory_faqs
uv run manage.py squashmigrations products 0002_faqcategory_faqs 0003_faqcategory_order

# Delete migrations and rename squash migrations to
0002_squash_0002_faqcategory_faqs.py -> 0002_faqcategory_faqs.py

# Validate the squash merge migraiton
uv run manage.py makemigration
uv run manage.py migrate

# Show migration
uv run manage.py showmigrations
```

# Django Browser Reload

```bash
uv run manage.py runserver
```

# Bootstrap 5 Tree View

https://github.com/nhmvienna/bs5treeview

# Load Plan

```bash
uv run manage.py loaddata plans
uv run manage.py loaddata plans

```
