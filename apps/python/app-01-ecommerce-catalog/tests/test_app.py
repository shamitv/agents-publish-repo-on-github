import unittest
import json
from app import app, db_conn

class App01TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_preseeded_products_retretrievable(self):
        response = self.app.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('products', data)
        self.assertTrue(len(data['products']) >= 8)

    def test_login_successful_with_valid_creds(self):
        payload = {'username': 'alice', 'password': 'alice123'}
        response = self.app.post('/api/auth/login', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'alice')

    def test_login_rejected_with_invalid_creds(self):
        payload = {'username': 'alice', 'password': 'wrong_password'}
        response = self.app.post('/api/auth/login', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

if __name__ == '__main__':
    unittest.main()
