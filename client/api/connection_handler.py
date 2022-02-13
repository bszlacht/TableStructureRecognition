import requests
import json


class ConnectionHandler:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.scheme = 'http://'

    def send(self, request, endpoint):
        data = request.content
        headers = request.headers
        url = self.scheme + str(self.ip) + ':' + self.port + endpoint

        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code == 201:
            return response.json()
        else:
            pass
