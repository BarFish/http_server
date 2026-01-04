import socket
import os
import re


IP = '0.0.0.0'
PORT = 8080
SOCKET_TIMEOUT = 5

WEBROOT = 'webroot'  # root directory
DEFAULT_URL = '/index.html'
UPLOAD_DIR = WEBROOT + '/uploads/'

FORBIDDEN_FILES = ['secret.txt']

REDIRECTION_DICTIONARY = {'/page1.html': '/page2.html'}

CONTENT_TYPES = {
    'html': 'text/html; charset=utf-8',
    'txt': 'text/html; charset=utf-8',
    'jpg': 'image/jpeg',
    'js': 'text/javascript; charset=UTF-8',
    'css': 'text/css'
}


def get_file_data(filename):
    """ Get data from file """
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f'Error: {e}')


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    try:
        lines = request.split('\r\n')
        request_line = lines[0]
        parts = request_line.split()

        if len(parts) != 3:
            return None, None

        method, url, version = parts

        if method not in ['GET', 'POST'] and not version.startswith('HTTP/'):
            return None, None

        return method, url

    except Exception as e:
        print(f'Error: {e}')
        return None, None


def handle_client_request(method: str, resource: str, client_socket, full_request_raw):
    """ Check the required resource, generate proper HTTP response and send to client"""
    try:
        # POST Image
        if method == 'POST' and '/upload' in resource:
            name_match = re.search(r'file-name=([\w.-]+)', resource)
            filename = name_match.group(1) if name_match else "uploaded_file.bin"

            header_end = full_request_raw.find(b'\r\n\r\n')
            body_data = full_request_raw[header_end + 4:]

            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)

            file_path = UPLOAD_DIR + filename
            with open(file_path, 'wb') as f:
                f.write(body_data)

            print(f"Uploaded and saved: {filename}")
            response = (
                "HTTP/1.0 200 OK\r\n"
                "Content-Length: 8\r\n\r\n"
                "Uploaded"
            ).encode()
            client_socket.send(response)
            return

        # GET Image
        image_match = re.search(r'/image\?image-name=([\w.-]+)', resource)
        if image_match:
            img_name = image_match.group(1)
            img_path = UPLOAD_DIR + img_name
            data = get_file_data(img_path)
            if data:
                header = (
                    f"HTTP/1.0 200 OK\r\n"
                    f"Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(data)}\r\n\r\n"
                ).encode()
                client_socket.send(header + data)
            else:
                client_socket.send("HTTP/1.0 404 Not Found\r\n\r\n".encode())
            return

        if resource == '' or resource == '/':
            filename = WEBROOT + DEFAULT_URL
        else:
            filename = WEBROOT + resource

        # Calculate next num
        num_pattern = re.compile(r'/calculate-next\?num=(?P<num>-?\d+)')
        num_match = num_pattern.match(resource)
        if num_match:
            num = int(num_match.group('num'))
            print(f'Calculate next num: num={num}')
            next_num = str(num + 1).encode()
            http_header = (
                "HTTP/1.0 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(next_num)}\r\n\r\n"
            ).encode()
            client_socket.send(http_header + next_num)
            return

        # Calculate area
        area_pattern = re.compile(r'/calculate-area\?height=(?P<height>-?\d*\.?\d+)&width=(?P<width>-?\d*\.?\d+)')
        area_match = area_pattern.match(resource)
        if area_match:
            height = float(area_match.group('height'))
            width = float(area_match.group('width'))
            print(f'Calculate area: height={height}&width={width}')
            area = str(height * width / 2).encode()
            http_header = (
                "HTTP/1.0 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(area)}\r\n\r\n"
            ).encode()
            client_socket.send(http_header + area)
            return

        # 302 Found
        if filename in REDIRECTION_DICTIONARY:
            redirect_url = REDIRECTION_DICTIONARY[filename]
            print(f"Redirecting {filename} to {redirect_url}")
            http_header = (
                "HTTP/1.1 302 Found\r\n"
                f"Location: {redirect_url}\r\n\r\n"
            ).encode()
            client_socket.send(http_header)
            return

        # 403 Forbidden
        if filename in FORBIDDEN_FILES:
            print(f"{resource} is forbidden.")
            response = (
                "HTTP/1.0 403 Forbidden\r\n\r\n"
            ).encode()
            client_socket.send(response)
            return

        # 404 Not Found
        if not os.path.isfile(filename):
            print(f"{filename} file not found")
            response = (
                "HTTP/1.0 404 Not Found\r\n\r\n"
            ).encode()
            client_socket.send(response)
            return

        # 200 OK
        data = get_file_data(filename)

        content_type = filename.split('.')[-1]
        if content_type in CONTENT_TYPES:
            content_type = CONTENT_TYPES[content_type]

        print('200 OK')
        http_header = (
            "HTTP/1.0 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(data)}\r\n\r\n"
        ).encode()

        http_response = http_header + data
        client_socket.send(http_response)
    except Exception as e:
        # 500 Internal Server Error
        print(f"Internal server error: {e}")
        response = (
            "HTTP/1.0 500 Internal Server Error\r\n\r\n"
        ).encode()
        client_socket.send(response)


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    while True:
        try:
            raw_request = b""
            while b'\r\n\r\n' not in raw_request:
                chunk = client_socket.recv(1024)
                if not chunk: break
                raw_request += chunk

            header_end = raw_request.find(b'\r\n\r\n')
            header_text = raw_request[:header_end].decode('utf-8', errors='ignore')
            method, resource = validate_http_request(header_text)

            if method == 'POST':
                length_match = re.search(r'Content-Length:\s*(\d+)', header_text, re.IGNORECASE)
                if length_match:
                    content_length = int(length_match.group(1))
                    while len(raw_request) < (header_end + 4 + content_length):
                        chunk = client_socket.recv(4096)
                        if not chunk: break
                        raw_request += chunk

            if resource is not None:
                print('Got a valid HTTP request')
                handle_client_request(method, resource, client_socket, raw_request)
            else:
                break
        except socket.timeout:
            print("Socket timeout")
            break
        except Exception as e:
            print(f'Error: {e}')
            break

    print('Closing connection')
    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    print("Listening for connections on port %d" % PORT)

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    main()
