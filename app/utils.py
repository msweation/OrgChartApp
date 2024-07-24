from google.cloud import bigquery, storage
import pandas as pd
import os
import json

def refresh_data():
    try:
        # Query the BigQuery database
        client = bigquery.Client()
        query = """
        SELECT *
        FROM IonSF.RecruitingOrgView
        """
        df = client.query(query).to_dataframe()

        # Save the DataFrame as a CSV file
        filepath = '/tmp/recruit_and_recruiter.csv'
        df.to_csv(filepath, index=False)

        # Upload CSV to GCS
        upload_to_gcs(filepath, 'recruit_and_recruiter.csv')

        # Build the hierarchy and save it as JSON
        hierarchy = build_hierarchy(df)
        hierarchy = convert_booleans_to_strings(hierarchy)
        
        json_filepath = '/tmp/org_chart.json'
        with open(json_filepath, 'w') as json_file:
            json.dump(hierarchy, json_file, indent=4)

        # Upload JSON to GCS
        upload_to_gcs(json_filepath, 'org_chart.json')
        
        return {'success': True}
    except Exception as e:
        print(f"Error refreshing data: {e}")
        return {'success': False, 'error': str(e)}

def build_hierarchy(df):
    df = df.sort_values(by=['Recruit', 'Recruiter', 'Recruit_Active', 'Total_Sales'], ascending=[True, True, False, False]).drop_duplicates(subset=['Recruit', 'Recruiter'], keep='first')
    
    unique_jobs = pd.unique(df[['Recruit', 'Recruiter']].values.ravel('K'))
    hierarchy = {}
    for name in unique_jobs:
        row = df[df['Recruit'] == name]
        if not row.empty:
            active_status = row['Recruit_Active'].iloc[0]
            sales = int(row['Total_Sales'].iloc[0])
            parent_name = row['Recruiter'].iloc[0] if pd.notna(row['Recruiter'].iloc[0]) else None
            hierarchy[name] = {
                'name': name,
                'children': [],
                'active': bool(active_status),
                'sales': sales,
                'parent': parent_name
            }
        else:
            hierarchy[name] = {
                'name': name,
                'children': [],
                'active': None,
                'sales': 0,
                'parent': None
            }

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
    

def extract_data(node, parent_name=None, data_list=[]):
    # Extract the current node's data
    data = {
        'Name': node.get('name'),
        'Parent': parent_name,
        'Active': node.get('active', None),
        'Sales': node.get('sales', 0)
    }
    data_list.append(data)
    
    # Recursively extract data for each child node
    for child in node.get('children', []):
        extract_data(child, node.get('name'), data_list)
    
    return data_list

def json_to_csv(json_data, temp_csv_filepath):
    root = json_data if 'children' in json_data else json_data['children'][0]
    data_list = extract_data(root)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data_list)

    # Save the DataFrame to a CSV file
    df.to_csv(temp_csv_filepath, index=False)
    return temp_csv_filepath

def upload_to_gcs(source_file, destination_blob):
    bucket_name = os.environ.get('GCS_BUCKET_NAME')
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(source_file)

def download_from_gcs(blob_name, destination_file):
    bucket_name = os.environ.get('GCS_BUCKET_NAME')
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(destination_file)

def load_local_json(filepath):
    with open(filepath, 'r') as json_file:
        return json.load(json_file)