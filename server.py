import socket
import os
import threading
from enum import Enum
from datetime import date
import sys

IP = "127.0.0.1"

# set http status messages
class HTTPStatusMessage(Enum):
    OK = "200 OK"
    BAD_REQUEST = "400 Bad Request"
    METHOD_NOT_ALLOWED = "405 Method Not Allowed"
    HTTP_VERSION_NOT_SUPPORTED = "505 HTTP Version Not Supported"
    NOT_FOUND = "404 Not Found"
    FORBIDDEN = "403 Forbidden"
    INTERNAL_SERVER_ERROR = "500 Internal Server Error"

class HTTPError(Exception):
    def __init__(self, message: HTTPStatusMessage):
        self.message = message

def main():
    args = sys.argv
    if len(args) != 3:
        raise('Invalid number of arguments, expected 2.')

    document_root = args[1]
    port = int(args[2])
    server_socket(document_root, port)

# handle client requests
def handle_client(conn, addr, document_root):
    with conn:
        print(f"New connection from {addr}")
        while True:
            try: 
                data = conn.recv(5000)
                if not data:
                    break

                (request, path, http_version) = parse_request(data.decode())
                print(f"Request: {request}, Path: {path}, HTTP Version: {http_version}")

                path = enhance_path(document_root, path)
                print(f'enhance_path: {path}')
                path_exists = validate_path(path)
                print(f'path_exists {path_exists}')
                if not path_exists:
                    continue

                content_type = get_content_type(path)
                content = get_file_content(path)

                conn.sendall(f"{http_version} {HTTPStatusMessage.OK._value_}\r\n".encode())
                conn.sendall(f"Date: {date.today()}\r\n".encode())
                conn.sendall(f"Content-Type: {content_type}\r\n".encode())

                # check http version to set connection header
                if http_version == "HTTP/1.1":
                    conn.sendall("Connection: keep-alive\r\n".encode())
                elif http_version == "HTTP/1.0":
                    conn.sendall("Connection: close\r\n".encode())

                if content_type not in ('image/png', 'image/x-icon'):
                    conn.sendall(f"Content-Length: {len(content.decode())}\r\n\r\n".encode())
                else:
                    conn.sendall("\r\n".encode())


                conn.sendall(content)

                if http_version == "HTTP/1.0":
                    print("Close connection")
                    conn.close()
            except HTTPError as e:
                print('HTTPError: ', str(e.message.value))
                conn.sendall(f"HTTP/1.0 {str(e.message.value)}\r\n\r\n".encode())

                conn.close()
            except Exception as e:
                print("Exception: ", e)
                conn.sendall(f"HTTP/1.0 {HTTPStatusMessage.INTERNAL_SERVER_ERROR}\r\n\r\n".encode())
                conn.close()


def parse_request(data: str):
    # change data to list of lines
    lines = data.splitlines()
    if len(lines) == 0:
        raise HTTPError(HTTPStatusMessage.BAD_REQUEST)
    components = lines[0].split(" ")
    if len(components) != 3:
        raise HTTPError(HTTPStatusMessage.BAD_REQUEST)
    elif components[0] != "GET":
        raise HTTPError(HTTPStatusMessage.METHOD_NOT_ALLOWED)
    elif components[2] not in ("HTTP/1.0", "HTTP/1.1"):
        raise HTTPError(HTTPStatusMessage.HTTP_VERSION_NOT_SUPPORTED)

    print("Before return in parse_request")
    return (components[0], components[1], components[2])


def get_file_content(path):
    with open(path, "rb") as f:
        return f.read()

def enhance_path(document_root: str, path: str):
    # print("Raw path: ", path)
    path = path.replace("%20", " ")
    if path in ("/", "/index.html"):
        path = f"{document_root}/index.html"
    else:
        path = f'{document_root}{path}'

    # print("Enhanced path: ", path)
    return path

def validate_path(path):
    # check if path exists
    path_exists = os.path.exists(path)

    if not path_exists:
        raise HTTPError(HTTPStatusMessage.NOT_FOUND)

    print("Path exists: ", path_exists)
    return path_exists

# get file content type to set content type header
def get_content_type(path):
    if path.endswith(".html"):
        return "text/html"
    elif path.endswith(".css"):
        return "text/css"
    elif path.endswith('.png'):
        return "image/png"
    elif path.endswith('.txt'):
        return "text/plain"
    elif path.endswith('.xml'):
        return "text/xml"
    elif path.endswith('.js'):
        return "application/javascript"
    elif path.endswith('.ico'):
        return "image/x-icon"
    elif path.endswith('.woff2'):
        return "font/woff2"
    else:
        return "text/plain"

def server_socket(document_root, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP, port))
    server.listen()
    print(f"Server is listening on {IP}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr, document_root)).start()

if __name__ == "__main__":
    main()