import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    if os.environ.get('GAE_ENV') == 'standard':  # Running on App Engine
        SQLALCHEMY_DATABASE_URI = (
            'mysql+pymysql://orgchartapp:IonSolar123@/OrgChart?unix_socket=/cloudsql/new-database-416522:us-central1:org-chart-database'
        )
    else:  # Running locally
        SQLALCHEMY_DATABASE_URI = (
            'mysql+pymysql://orgchartapp:IonSolar123@127.0.0.1:3306/OrgChart'
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
    LOCAL_JSON_PATH = '/tmp/org_chart.json'
