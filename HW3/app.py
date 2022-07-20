import socketserver
import sys


def readFile(filename):
    try:
        with open(filename, "rb") as f:
            fileData = f.read()
            return fileData
    except FileNotFoundError as error:
        return -1


# Only writes into images folder
def writeFile(filename, data):
    with open(filename, "wb") as f:
        f.write(data)


def replaceHomepage():
    # Insert names and comments
    html = readFile("index.html").decode()
    skeleton = "<p> data </p>"
    replacement = ""
    for val in comment_data:
        split = val.split("\n")
        replacement += skeleton.replace("data", "<b>Name:</b> " + split[0] + " <b>Comment:</b> " + split[1])
    html = html.replace('''<div id="comments"></div>''', replacement)

    # Insert images and captions
    replacement = ""
    for val in caption_data:
        split = val.split("\n")
        replacement += skeleton.replace("data", "<b>Caption:</b> " + split[0] + split[1])
    html = html.replace('''<div id="pictures"></div>''', replacement)

    return html.encode()


def escapeHTML(html):
    html = html.replace('&', "&amp").replace('<', "&lt").replace('>', "&gt").replace("\\", "")
    return html


comment_data = []
caption_data = []


class MyTCPHandler(socketserver.BaseRequestHandler):
    global comment_data
    global caption_data

    def handle(self):
        received_data = self.request.recv(1024)
        # print(received_data)
        # print(self.client_address[0] + " is sending data:")
        #print(received_data.decode() + "\n\n")
        self.parseHTTP(received_data)
        sys.stdout.flush()

    def parseHTTP(self, received_data):
        if received_data:
            # Decode received_data if content is not in it
            try:
                # Checks if content is in received_data
                split_point = (0, received_data.index("\r\n\r\n".encode()))
            except ValueError:
                split_point = (1, 0)
            if split_point[0] == 0:  # content IS in received Data
                # Split received_data into (headers, content)
                headers = received_data[:split_point[1]].decode()
                content = received_data[split_point[1]:]
            else:  # content IS NOT in received Data
                headers = received_data.decode()
                content = b''

            # Split headers into individual header lines
            split_headers = headers.split("\r\n")
            # Get Content-Length and Content-Type lines from split_headers
            headers_targets = ["Content-L", "Content-T"]
            headers_content = []
            for header in split_headers:
                if any(x in header for x in headers_targets):
                    headers_content.append(header)
            content_length = 0
            if headers_content:
                content_length = int(headers_content[0][headers_content[0].find(":") + 2:])
                # print(content_length)

            # Retrieve rest of content if not already retrieved
            while len(content) < content_length:
                content += self.request.recv(1024)
            print(len(content))

            # Split request line to get /path
            request_line = split_headers[0].split()
            path = request_line[1]
            # Check for jpg extension
            extension = path[path.find("."):]

            # GET Responses
            if request_line[0] == "GET":
                if path == "/":
                    self.createResponse_200("text/html", replaceHomepage())
                elif path == "/functions.js":
                    self.createResponse_200("text/javascript", readFile("functions.js"))
                elif path == "/style.css":
                    self.createResponse_200("text/css", readFile("style.css"))
                elif path[:7] == "/images" and extension == ".jpg":
                    data = readFile(path[1:])
                    if data != -1:
                        self.createResponse_200("image/jpeg", data)
                    else:
                        self.createResponse_404()
                else:
                    self.createResponse_404()

            # POST Responses
            elif request_line[0] == "POST":
                content_type = "multipart/form-data"
                # Locate boundary string and remove quotes
                boundary_string = headers_content[1][headers_content[1].find("boundary=") + 9:]
                boundary_string = ("--" + boundary_string.replace('"', "")).encode()

                # Split content by boundary and add each split to split_content list
                split_contents = content.split(boundary_string)
                # print(".....................Length of split_contents: " + str(len(split_contents)))
                # print(content)
                if path == "/comment":
                    # Separate headers from content in each boundary
                    bound_A = split_contents[1].decode().split("\r\n\r\n", 1)
                    contentA = escapeHTML(bound_A[1].replace("\r\n", ""))
                    bound_B = split_contents[2].decode().split("\r\n\r\n", 1)
                    contentB = escapeHTML(bound_B[1].replace("\r\n", ""))
                    # Check name header in each boundary and save the data in the format (name + comment)
                    if bound_A[0].find('''name="name"''') != -1:
                        comment_data.append(contentA + "\n" + contentB)
                    else:
                        comment_data.append(contentB + "\n" + contentA)
                    # Reload user's page to update data
                    self.createResponse_301("/")
                if path == "/image-upload":
                    # Separate headers from content in each boundary
                    bound_A = split_contents[1].split("\r\n\r\n".encode(), 1)

                    bound_B = split_contents[2].split("\r\n\r\n".encode(), 1)
                    head_A = bound_A[0].decode()
                    if head_A.find('''name="name"''') != -1:
                        contentA = escapeHTML(bound_A[1].decode().replace("\r\n", ""))
                        self.saveFile(bound_B[0].decode(), bound_B[1], contentA)
                    else:
                        contentA = escapeHTML(bound_B[1].decode().replace("\r\n", ""))
                        self.saveFile(bound_A[0].decode(), bound_A[1], contentA)
        else:
            self.createResponse_404()

    # Saves png to images folder
    def saveFile(self, input_header, file_data, name):
        filename_start = input_header.find("filename=") + 10
        filename_end = filename_start
        while input_header[filename_end] != '"':
            filename_end += 1
        filename = "images/" + input_header[filename_start:filename_end].replace('/', "").replace('~', "")
        if filename != "images/":
            writeFile(filename, file_data)
            caption_data.append(name + "\n" + '<br><img src="/' + filename + '"/>')
        self.createResponse_301("/")

    # Handles the creation of all 200 HTTP responses
    # Assumes body is already encoded
    def createResponse_200(self, MIMEType, body):
        # Response is separated into specified sections
        response = "HTTP/1.1 200 OK"
        contentType = "\r\nContent-Type: " + MIMEType + "; charset=utf-8"
        noSniff = "\r\nX-Content-Type-Options: nosniff"
        contentLength = "\r\nContent-Length: " + str(len(body)) + "\r\n\r\n"

        # Combines all sections for complete response
        response += contentType + noSniff + contentLength
        self.request.sendall(response.encode() + body)

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


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()
