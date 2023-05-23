import requests

class InternetAccess:
    def __init__(self):
        self.session = requests.Session()

    def request(self, method, url, headers=None, params=None, data=None, json=None, auth=None):
        response = self.session.request(method, url, headers=headers, params=params, data=data, json=json, auth=auth)
        return response