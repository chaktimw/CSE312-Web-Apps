import mysql.connector
import socketserver
import sys
import hashlib
import base64
import os


# mysql DB
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
db = mysql.connector.connect(user=DB_USERNAME, password=DB_PASSWORD, host='mysql', database='chatlogs')
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS messages (username TEXT, message TEXT)")


def addMessageDB(payload):
    statement = "INSERT INTO messages (username, message) VALUES (%s, %s)"
    user_pos = payload.find(b'username') + 11
    mes_pos = payload.find(b'"comment')
    username = payload[user_pos: mes_pos - 2].decode()
    message = payload[mes_pos + 11: payload.find(b'}') - 1].decode()
    values = (username, message)
    print(values)
    cursor.execute(statement, values)
    db.commit()


def readMessages():
    cursor.execute("SELECT * FROM messages")
    data = cursor.fetchall()
    messages = []
    for row in data:
        encoded_message = ('{"username":"' + row[0] + '","comment":"' + row[1] + '"}').encode()
        messages.append(createFrame(encoded_message))
    return messages


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


def parseFrame(frame):
    bit_array = []
    for x in frame:
        value = bin(x)[2:]
        while len(value) < 8:
            value = '0' + value
        bit_array.append(value)
    # print(bit_array)
    # fin bit and 3 rsv assumed to be 1000
    opcode = bit_array[0][4:]
    mask_bit = bit_array[1][0]
    payload_len = int(bit_array[1][1:], 2)
    # Increase payload_len if limit reached
    current_index = 2
    if payload_len == 126:
        payload_len = int(bit_array[2] + bit_array[3], 2)
        current_index = 4
    elif payload_len == 127:
        payload_len = int(''.join(bit_array[2:10]), 2)
        current_index = 10
    # Get mask if indicated in mask bit
    mask = ''
    if mask_bit == '1':
        mask = ''.join(bit_array[current_index:current_index+4])
        current_index += 4
    # Read payload 4 bytes at a time
    payload = ""
    payload_to_be_read = payload_len
    while payload_to_be_read > 0:
        if payload_to_be_read < 4:
            temp = ''.join(bit_array[current_index:current_index+payload_to_be_read])
            payload_to_be_read = 0
        else:
            temp = ''.join(bit_array[current_index:current_index+4])
            current_index += 4
            payload_to_be_read -= 4
        if mask_bit == '1':
            masked_bytes = bin(int(mask[:len(temp)], 2) ^ int(temp, 2))[2:]
            while len(masked_bytes) % 8 != 0:
                masked_bytes = '0' + masked_bytes
            payload += masked_bytes
        else:
            payload += temp
    return encodePayload(payload)


def encodePayload(payload):
    currentIndex = 0
    encoded_payload = b''
    for a in range(len(payload) // 8):
        encoded_payload += int(payload[currentIndex:currentIndex+8], 2).to_bytes(1, byteorder='big')
        currentIndex += 8
    # Escape html
    encoded_payload = escapeHTML(encoded_payload.decode()).encode()
    return encoded_payload


def createFrame(payload):
    # Initial byte
    frame = int("10000001", 2).to_bytes(1, byteorder='big')

    # Create payload_length with mask_bit = 0
    payload_len = len(payload)
    if payload_len < 126:
        payload_len = bin(payload_len)[2:]
        while len(payload_len) < 8:
            payload_len = '0' + payload_len
    elif payload_len < 65536:
        initial = "01111110"
        payload_len = bin(payload_len)[2:]
        while len(payload_len) < 16:
            payload_len = '0' + payload_len
        payload_len = initial + payload_len
    else:
        initial = "01111111"
        payload_len = bin(payload_len)[2:]
        while len(payload_len) < 64:
            payload_len = '0' + payload_len
        payload_len = initial + payload_len

    # Convert payload_length to bytes and add to frame
    currentIndex = 0
    for a in range(len(payload_len) // 8):
        frame += int(payload_len[currentIndex:currentIndex+8], 2).to_bytes(1, byteorder='big')
        currentIndex += 8
    # Add payload
    frame += payload
    return frame


comment_data = []
caption_data = []
clients = []
client_sockets = []


class MyTCPHandler(socketserver.BaseRequestHandler):
    global comment_data
    global caption_data
    global clients
    global client_sockets

    def handle(self):
        client_id = ""
        try:
            while True:
                received_data = self.request.recv(1024)
                client_id = self.client_address[0] + ":" + str(self.client_address[1])
                print(client_id + " is sending data:")
                # print(received_data.decode() + "\n\n")
                self.parseHTTP(received_data)
                sys.stdout.flush()
        except Exception as error:
            print(error)
            if client_id in clients:
                client_index = clients.index(client_id)
                clients.pop(client_index)
                client_sockets.pop(client_index)
            print("---Connection Closed-----")
            print(clients)
            pass

    def parseHTTP(self, received_data):
        client_id = self.client_address[0] + ":" + str(self.client_address[1])
        if received_data:
            if client_id in clients:
                repacked_data = createFrame(parseFrame(received_data))
                addMessageDB(repacked_data)
                for x in client_sockets:
                    x.sendall(repacked_data)
            else:
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

                # Split headers into individual header lines and store them in a dictionary
                headers_dict = {}
                split_headers = headers.split("\r\n")
                for header in split_headers:
                    colon_pos = header.find(":")
                    if colon_pos != -1:
                        headers_dict[header[0:colon_pos]] = header[colon_pos + 2:]
                # Get Content-Length
                content_length = 0
                if "Content-Length" in headers_dict:
                    content_length = int(headers_dict["Content-Length"])

                # Retrieve rest of content if not already retrieved
                while len(content) < content_length:
                    content += self.request.recv(1024)

                # Split request line to get /path
                request_line = split_headers[0].split()
                path = request_line[1]
                print(path)
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
                    elif path == "/websocket":
                        if client_id not in clients:
                            clients.append(client_id)
                            client_sockets.append(self.request)
                        print(clients)
                        key = headers_dict["Sec-WebSocket-Key"]
                        self.createResponse_101(key)
                        for message in readMessages():
                            self.request.sendall(message)
                    else:
                        self.createResponse_404()

                # POST Responses
                elif request_line[0] == "POST":
                    content_type = "multipart/form-data"
                    # Locate boundary string and remove quotes
                    bound_source = headers_dict["Content-Type"]
                    boundary_string = bound_source[bound_source.find("boundary=") + 9:]
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
        location = "\r\nLocation: " + newLocation + "\r\n\r\n"
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

    # Handles websocket upgrades 101 response
    def createResponse_101(self, key):
        response = "HTTP/1.1 101 Switching Protocols"
        Connection = "\r\nConnection: Upgrade"
        Upgrade = "\r\nUpgrade: websocket"
        key_bytes = (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
        key_hash = base64.b64encode(hashlib.sha1(key_bytes).digest())
        key_line = "\r\nSec-WebSocket-Accept: "

        # Combines all sections for complete response
        response += Connection + Upgrade + key_line
        self.request.sendall(response.encode() + key_hash + "\r\n\r\n".encode())


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()
