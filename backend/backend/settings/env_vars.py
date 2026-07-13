# Use 12factor inspired environment variables or from a file
import os
from pathlib import Path

import environ
env = environ.Env()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

if os.environ.get('DJANGO_ENVIRONMENT') == 'Container':
    environ.Env.read_env()
else:
    env_file = BASE_DIR.joinpath('backend', 'settings', 'local.env')
    if os.path.exists(env_file):
        environ.Env.read_env(str(env_file))
