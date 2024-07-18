def build_org_chart(data):
    def build_tree(df, parent_id):
        tree = []
        for _, row in df[df['ParentID'] == parent_id].iterrows():
            children = build_tree(df, row['ID'])
            tree.append({
                'id': row['ID'],
                'name': row['Name'],
                'children': children
            })
        return tree

    root_nodes = data[data['ParentID'].isnull()]
    org_chart = []
    for _, row in root_nodes.iterrows():
        children = build_tree(data, row['ID'])
        org_chart.append({
            'id': row['ID'],
            'name': row['Name'],
            'children': children
        })
    return org_chart
