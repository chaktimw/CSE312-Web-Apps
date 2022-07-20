import socketserver
import sys


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_data = self.request.recv(1024).strip()
        print(self.client_address[0] + " is sending data:")
        # print(received_data)
        # print(received_data.decode())
        print("\n\n")
        decoded_data = received_data.decode()
        self.parseHTTP(decoded_data)
        sys.stdout.flush()

    def parseHTTP(self, received_data):
        split_data = received_data.split("\r\n")
        request_line = split_data[0].split()
        if request_line[0] == "GET":
            # if request_line[1] == "/":
            #    self.default()
            if request_line[1] == "/hello":
                self.hello()
            elif request_line[1] == "/hi":
                self.hi()
            else:
                self.notFound()

    # def default(self):
    #     self.request.sendall(
    #         """HTTP/1.1 200 OK\r\n
    #         Content-Type: text/plain\r\n
    #         Content-Length: 19\r\n\r\n
    #         Welcome to my site!""".encode())

    def hello(self):
        self.request.sendall(
            "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 12\r\n\r\nHello, user!".encode())

    def hi(self):
        self.request.sendall(
            "HTTP/1.1 301 Moved permanently\r\nLocation: /hello".encode())

    def notFound(self):
        self.request.sendall(
            "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 36\r\n\r\nThe requested content does not exist".encode())


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()
