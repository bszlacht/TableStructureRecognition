from ..input.DataInstance import DataInstance
from ..input.ModelBuilder import Model

from ipaddress import ip_address
from urllib.parse import urlparse

from client.api.request import Request
from client.api.connection_handler import ConnectionHandler


class Service:

    def __init__(self, address):
        ip, port = self.parse_ip_port(address)
        self.handler = ConnectionHandler(ip, port)

    def predict(self, model: Model, data_instance: DataInstance):
        request = Request(model, data_instance)
        result = self.handler.send(request, "/predict")
        print(result)

    @staticmethod
    def parse_ip_port(address):
        try:
            ip = ip_address(address)
            port = None
        except ValueError:
            parsed = urlparse('//{}'.format(address))
            ip = ip_address(parsed.hostname)
            port = parsed.port
        return ip, port


# code for test

if __name__ == "__main__":
    address = "127.0.0.1:80"
    service = Service(address)
    ip, port = service.parse_ip_port(address)
    print(ip)
    print(port)
