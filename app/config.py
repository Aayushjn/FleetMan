import os
from pathlib import Path


BASE_DIR = Path(__file__).parent.absolute()


class Config:
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
