from google.cloud import bigquery
import pandas as pd
import os
import json

def refresh_data(upload_folder):
    try:
        # Query the BigQuery database
        client = bigquery.Client()
        query = """
        SELECT *
        FROM IonSF.RecruitingOrgView
        """
        df = client.query(query).to_dataframe()

        # Save the DataFrame as a CSV file
        filepath = os.path.join(upload_folder, 'recruit_and_recruiter.csv')
        df.to_csv(filepath, index=False)

        # Build the hierarchy and save it as JSON
        hierarchy = build_hierarchy(df)
        hierarchy = convert_booleans_to_strings(hierarchy)
        
        json_filepath = os.path.join(upload_folder, 'org_chart.json')
        with open(json_filepath, 'w') as json_file:
            json.dump(hierarchy, json_file, indent=4)
        
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
