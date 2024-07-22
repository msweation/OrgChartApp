import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@"
        f"/{os.environ.get('DB_NAME')}?unix_socket=/cloudsql/{os.environ.get('DB_CONNECTION_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME') or 'org-chart-app-storage'
