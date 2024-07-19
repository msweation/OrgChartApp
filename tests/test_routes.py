import unittest
from app import create_app
import pandas as pd
import json

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_index(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_upload_file(self):
        data = {
            'Recruit': ['A', 'B', 'C', 'D'],
            'Recruiter': [None, 'A', 'A', 'B'],
            'Recruit_Active': [1, 1, 0, 1],
            'Total_Sales': [100, 200, 150, 50]
        }
        df = pd.DataFrame(data)
        df.to_csv('test_recruit_and_recruiter.csv', index=False)

        with open('test_recruit_and_recruiter.csv', 'rb') as f:
            result = self.app.post('/upload', data={'file': f})

        self.assertEqual(result.status_code, 200)
        self.assertIn('Root', result.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
