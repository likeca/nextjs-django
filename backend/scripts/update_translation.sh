# Create the message file
# source $PWD/.venv/bin/activate && ./src/manage.py makemessages -l fr --pythonpath $PWD/nextjs_django
# source $PWD/.venv/bin/activate && ./src/manage.py makemessages -l zh-cn --pythonpath $PWD/nextjs_django

# Update existing messages file, execute from nextjs_django/scripts/
PROJECT_PATH=$PWD
cd src
source $PROJECT_PATH/.venv/bin/activate && ./manage.py makemessages -a

# Use django-autotranslate to translate po file
source $PROJECT_PATH/.venv/bin/activate && ./manage.py translate_messages -u -f

# Compile po file for production
source $PROJECT_PATH/.venv/bin/activate && ./manage.py compilemessages


# source $PWD/.venv/bin/activate && ./src/manage.py translate_messages [options]
# -f, --set-fuzzy: Set the 'fuzzy' flag on autotranslated entries
# -l, --locale 'locale': Only translate the specified locales
# -u, --untranslated: Only translate the untranslated messages

# Django translation in template
# Force variables to be translated
# In views.py
# def my_view(request):
#     return render(request, 'i18n_test.html', {'salutation':_("Hola")})
# In html (Complex sentences)
# {% blocktrans %}This string will have {{ value }} inside.{% endblocktrans %}
# {% blocktrans with book_t=book|title author_t=author|title %}
#     This is {{ book_t }} by {{ author_t }}
# {% endblocktrans %}