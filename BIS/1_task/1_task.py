import requests
import json
import unittest

class User():
    def __init__(self):
        self.base_url = 'https://petstore.swagger.io/v2/user'
        self.headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
            }

    def create_user(self, user):
        url = self.base_url
        user_json = json.dumps(user)
        res  = requests.post(url, data = user_json, headers=self.headers)
        return res 

    def get_user(self, user_name):
        url = self.base_url + '/' + user_name
        res  = requests.get(url, headers=self.headers)
        return res

    def update_user(self, user_name, user):
        url = self.base_url + '/' + user_name
        user_json = json.dumps(user)
        res  = requests.put(url, data = user_json, headers=self.headers)
        return res

    def delete_user(self, user_name):
        url = self.base_url + '/' + user_name
        res  = requests.delete(url, headers=self.headers)
        return res

class TestUserCrud(unittest.TestCase):
    def setUp(self):
        self.api_class = User()
        self.test_user = {
        'id': '0',
        'username':'username_3',
        'firstName':'Sasha',
        'lastName':'Petrov',
        'email':'546@mail.ru',
        'password':'123456',
        'phone':'+45 789 45 45',
        'userStatus': 1,
        }

    def test_create(self):
        res = self.api_class.create_user(self.test_user)
        if res.ok:
            self.api_class.delete_user(self.test_user['username'])
        self.assertTrue(res.ok)

    def test_get(self):
        res0 = self.api_class.create_user(self.test_user)
        res = self.api_class.get_user(self.test_user['username'])
        if res.ok:
            self.api_class.delete_user(self.test_user['username'])
        self.assertTrue(res.ok)

    def test_update(self):
        res0 = self.api_class.create_user(self.test_user)
        res = self.api_class.update_user(self.test_user['username'], self.test_user)
        if res.ok:
            self.api_class.delete_user(self.test_user['username'])
        self.assertTrue(res.ok)

    def test_delete(self):
        res0 = self.api_class.create_user(self.test_user)
        res = self.api_class.delete_user(self.test_user['username'])
        if res.ok:
            self.api_class.delete_user(self.test_user['username']) 
        self.assertTrue(res.ok)

if __name__ == '__main__':
    unittest.main()


    