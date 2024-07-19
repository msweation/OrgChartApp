import unittest
import pandas as pd
from app.utils import build_hierarchy, convert_booleans_to_strings

class UtilsTestCase(unittest.TestCase):
    def test_build_hierarchy(self):
        data = {
            'Recruit': ['A', 'B', 'C', 'D'],
            'Recruiter': [None, 'A', 'A', 'B'],
            'Recruit_Active': [1, 1, 0, 1],
            'Total_Sales': [100, 200, 150, 50]
        }
        df = pd.DataFrame(data)
        hierarchy = build_hierarchy(df)
        self.assertEqual(hierarchy['children'][0]['name'], 'A')
        self.assertEqual(hierarchy['children'][0]['children'][0]['name'], 'B')

    def test_convert_booleans_to_strings(self):
        data = {'name': 'A', 'active': True, 'children': []}
        converted = convert_booleans_to_strings(data)
        self.assertEqual(converted['active'], 'true')

if __name__ == '__main__':
    unittest.main()
