from django.test import Client, TestCase
import json


class AccountTests(TestCase):

    def test_registration(self):
        data = {
            'email': 'foo@example.com',
            'password': 'test1234',
            'username': 'foo'
        }
        result = Client().post(
            '/accounts/', json.dumps(data), content_type='application/json')
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json().get('email'), data['email'])
        self.assertEqual(result.json().get('username'), data['username'])
        self.assertNotIn('password', result.json())
