import json

import requests

class Scloud():
    def __init__(self):
        self.curl = requests.session()
        self.curl.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        }

    def login(self):
        url = 'https://api.cybree.com/v1/account/login_by_password'
        data = {
            'email': 'fz58358@gmail.com',
            'password': 'KPqH2YbYHXZ3kJg'
        }
        result = self.curl.post(url, data=json.dumps(data))
        print(result.text)

        print(self.curl.get('https://api.cybree.com/v1/balance').json())

if __name__ == '__main__':
    sApi = Scloud()
    sApi.login()

