import socketserver
import sys


def readFile(filename):
    with open(filename, "rb") as f:
        fileData = f.read()
    return fileData


class MyTCPHandler(socketserver.BaseRequestHandler):
\\
    def handle(self):
        received_data = self.request.recv(1024).strip()
        print(self.client_address[0] + " is sending data:")
        # print(received_data.decode())
        decoded_data = received_data.decode()
        self.parseHTTP(decoded_data)
        sys.stdout.flush()

    def parseHTTP(self, received_data):
        # Read received_data
        split_data = received_data.split("\r\n")
        request_line = split_data[0].split()
        path = request_line[1]

        # Check if path contains a file
        extensionIndex = path.find(".")

        # Depending on the path, create a response
        if request_line[0] == "GET":
            if path == "/":
                self.createResponse_200("text/html", readFile("index.html"), 1)
            elif extensionIndex != -1:
                extension = path[extensionIndex:]
                if extension == ".txt":
                    self.createResponse_200("text/plain", readFile(path[1:]), 1)
                elif extension == ".css":
                    self.createResponse_200("text/css", readFile(path[1:]), 1)
                elif extension == ".jpg":
                    self.createResponse_200("image/jpeg", readFile(path[1:]), 1)
                elif extension == ".js":
                    self.createResponse_200("text/javascript", readFile(path[1:]), 1)
                else:
                    self.createResponse_404()
            elif path[:8] == "/images?":
                self.createHTML(path[8:])
            else:
                self.createResponse_404()

    # Handles the creation of all 200 HTTP responses
    def createResponse_200(self, MIMEType, body, bodyEncoded):
        # Response is separated into specified sections
        response = "HTTP/1.1 200 OK"
        contentType = "\r\nContent-Type: " + MIMEType + "; charset=utf-8"
        noSniff = "\r\nX-Content-Type-Options: nosniff"

        # Encodes the body so the length can be determined (does not encode files)
        encodedContent = body
        if not bodyEncoded:
            encodedContent = body.encode()

        # Content length is determined by number of bytes in encoded body
        contentLength = "\r\nContent-Length: " + str(len(encodedContent)) + "\r\n\r\n"
        response += contentType + noSniff + contentLength
        result = response.encode() + encodedContent
        # print(result)
        self.request.sendall(result)

    # Handles the creation of 301 redirect responses
    def createResponse_301(self, newLocation):
        response = "HTTP/1.1 301 Moved permanently"
        location = "\r\nLocation: " + newLocation
        response += location
        self.request.sendall(response.encode())

    # Handles the creation of 404 Not Found error response
    def createResponse_404(self):
        body = "The requested content does not exist."
        response = "HTTP/1.1 404 Not Found"
        contentType = "\r\nContent-Type: " + "text/plain"
        noSniff = "\r\nX-Content-Type-Options: nosniff"
        contentLength = "\r\nContent-Length: " + str(len(body))
        content = "\r\n\r\n" + body
        response += contentType + noSniff + contentLength + content
        self.request.sendall(response.encode())

    # Creates an html page with all of the listed pictures
    # ASSUMES the request is in the proper format
    def createHTML(self, input):
        query = input.split("&")
        nameIndex = 1
        imagesIndex = 0
        if query[0][:5] == "name=":
            nameIndex = 0
            imagesIndex = 1
        name = query[nameIndex][5:]
        listOfImages = query[imagesIndex][7:].split("+")

        # List of user requested pics in html format
        imagesHTMLSkeleton = "<img src=image_filename/>"
        imagesHTML = ""
        for x in listOfImages:
            imagesHTML += imagesHTMLSkeleton.replace("image_filename", "\"image/" + x + ".jpg\"")

        # HTML
        html = """<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>Custom Pics</title>
        </head>
        <body>
        <h1>""" + "Welcome, " + name + "!" + """</h1>
        """ + imagesHTML + """
        </body>
        </html>"""
        print(html)
        # Send Request
        self.createResponse_200("text/html", html.encode(), 1)


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()
