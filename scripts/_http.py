import httpx

class HTTPClient(object):
    def __init__(self, port: int) -> None:
        self.host = "http://localhost"
        self.port = port

    def exec_request(self, endpoint):
        with httpx.Client() as client:
            response = client.request("GET", "{}:{}{}".format(self.host, self.port, endpoint))
            response.raise_for_status()
            return response.json()