import requests
import json


class ConnectionHandler:

    def __init__(self, ip, port, scheme='http://'):
        self.ip = ip
        self.port = port
        self.scheme = scheme

    @property
    def url(self) -> str:
        return f'{self.scheme}{self.ip}:{self.port}'

    def send(self, request, endpoint):
        data = request.content
        headers = request.headers
        url = self.url + endpoint

        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return -1
