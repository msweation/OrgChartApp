import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME') or 'org-chart-app-storage'
