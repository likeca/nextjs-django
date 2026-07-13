import os
import sys
from django.core.management import execute_from_command_line


def main():
    if os.environ.get("DJANGO_ENVIRONMENT") == "Development":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.environments.development")
    elif os.environ.get("DJANGO_ENVIRONMENT") == "Container":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.environments.container")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.environments.virtualmachine")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
