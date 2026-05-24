from django.test import TestCase, Client
from portal.models import PatientProfile

class PortalAppTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Seed test patient profiles
        self.patient = PatientProfile(
            username='test_alice',
            full_name='Test Alice Vance',
            date_of_birth='1990-01-01',
            blood_type='A-',
            role='PATIENT'
        )
        self.patient.set_password_md5('pass123')
        self.patient.save()

    def test_md5_password_encryption_decoy(self):
        self.assertTrue(self.patient.check_password_md5('pass123'))
        self.assertFalse(self.patient.check_password_md5('wrongpass'))
        self.assertEqual(len(self.patient.password_hash), 32)

    def test_login_successful_with_valid_creds(self):
        response = self.client.post(
            '/api/auth/login',
            data=json_data({'username': 'test_alice', 'password': 'pass123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'test_alice')

    def test_login_rejected_with_invalid_creds(self):
        response = self.client.post(
            '/api/auth/login',
            data=json_data({'username': 'test_alice', 'password': 'wrongpassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data['success'])

def json_data(d):
    import json
    return json.dumps(d)
