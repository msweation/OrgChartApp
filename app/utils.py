import pandas as pd

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
