# utils.py
from google.cloud import bigquery, storage
import pandas as pd
from flask import current_app
import os
import json

def refresh_data():
    client = bigquery.Client()
    query = """
    SELECT *
    FROM IonSF.RecruitingOrgView
    """
    df = client.query(query).to_dataframe()
    
    storage_client = storage.Client()
    bucket_name = current_app.config['GCS_BUCKET_NAME']
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('recruit_and_recruiter.csv')

    temp_file_path = '/tmp/recruit_and_recruiter.csv'
    df.to_csv(temp_file_path, index=False)
    
    # Upload CSV to Google Cloud Storage
    blob.upload_from_filename(temp_file_path)
    
    # Read the CSV file from the temporary directory
    data = pd.read_csv(temp_file_path)
    hierarchy = build_hierarchy(data)
    hierarchy = convert_booleans_to_strings(hierarchy)
    
    json_blob = bucket.blob('org_chart.json')
    json_blob.upload_from_string(json.dumps(hierarchy, indent=4), content_type='application/json')
    
    return {"status": "success", "message": "Data refreshed successfully"}

def build_hierarchy(df):
    df = df.sort_values(by=['Recruit', 'Recruiter', 'Recruit_Active', 'Total_Sales'], ascending=[True, True, False, False]).drop_duplicates(subset=['Recruit', 'Recruiter'], keep='first')
    
    unique_jobs = pd.unique(df[['Recruit', 'Recruiter']].values.ravel('K'))
    hierarchy = {}
    for name in unique_jobs:
        row = df[df['Recruit'] == name]
        if not row.empty:
            active_status = row['Recruit_Active'].iloc[0]
            sales = int(row['Total_Sales'].iloc[0])
            hierarchy[name] = {'name': name, 'children': [], 'active': bool(active_status), 'sales': sales}
        else:
            hierarchy[name] = {'name': name, 'children': [], 'active': None, 'sales': 0}

    for _, row in df.iterrows():
        recruit, recruiter = row['Recruit'], row['Recruiter']
        if pd.notna(recruiter):
            hierarchy[recruiter]['children'].append(hierarchy[recruit])

    top_levels = [hierarchy[row['Recruit']] for _, row in df.iterrows() if pd.isna(row['Recruiter'])]
    return {'name': 'Root', 'children': top_levels}

def convert_booleans_to_strings(d):
    if isinstance(d, dict):
        return {k: convert_booleans_to_strings(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_booleans_to_strings(i) for i in d]
    elif isinstance(d, bool):
        return str(d).lower()
    else:
        return d
