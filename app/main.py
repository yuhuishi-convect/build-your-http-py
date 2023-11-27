# Uncomment this to pass the first stage
import socket
from dataclasses import dataclass
import re
import threading
import argparse
import os.path
import os

@dataclass
class Request:
    method: str
    path: str
    headers: dict
    body: str


@dataclass
class Response:
    status: str
    headers: dict
    body: str


def respond(client_socket, response: Response):
    """
    Send the response to the client
    """
    if response.status == "404":
        respond_404(client_socket)

    headline = f"HTTP/1.1 {response.status}\r\n"
    headers = "\r\n".join([f"{key}: {value}" for key, value in response.headers.items()])
    body = response.body
    response = headline + headers + "\r\n\r\n" + body
    client_socket.send(response.encode())

def respond_404(client_socket):
    response = "HTTP/1.1 404 Not Found\r\n\r\n"
    client_socket.send(response.encode())


def read_request(client_socket) -> Request:
    buffer_size = 1024
    request = client_socket.recv(buffer_size).decode()

    # extract the path from the request
    """
    The request has the form 
    GET /index.html HTTP/1.1

    Host: localhost:4221
    User-Agent: curl/7.64.1

    """

    # split the request into lines
    lines = request.split("\r\n")
    # extract the path from the first line
    path = lines[0].split()[1]
    # parse the headers information
    headers = {}
    header_pattern = re.compile(r"^(.*): (.*)$")
    for line in lines[1:]:
        if line == "":
            break
        key, value = header_pattern.match(line).groups()
        headers[key] = value.strip()
    return Request(method="GET", path=path, headers=headers, body="")


def echo_handler(request: Request) -> Response:
    message = request.path.split("/echo/")[1]
    return Response(status="200 OK", headers={
        "Content-Type": "text/plain",
        "Content-Length": str(len(message))
    }, body=message)


def user_agent_handler(request: Request) -> Response:
    # return the user agent in the body
    user_agent = request.headers["User-Agent"]
    return Response(status="200 OK", headers={
        "Content-Type": "text/plain",
        "Content-Length": str(len(user_agent))
    }, body=user_agent)


def file_handler(request: Request, directory: str) -> Response:
    # return the file content in the body
    # the path is in the form /file/<filename>
    filename = request.path.split("/files/")[1]
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        return Response(status="404", headers={}, body="")

    with open(file_path, "r") as f:
        content = f.read()
    return Response(status="200 OK", headers={
        "Content-Type": "text/plain",
        "Content-Length": str(len(content))
    }, body=content)



def router(request: Request, directory: str) -> Response:
    print(request)
    if request.path == "/":
        return Response(status="200 OK", headers={}, body="")
    elif request.path.startswith("/echo"):
        return echo_handler(request)
    elif request.path == "/user-agent":
        return user_agent_handler(request)
    elif request.path.startswith("/files"):
        return file_handler(request, directory)
    else:
        return Response(status="404", headers={}, body="")


def handle_client(client_socket, directory_to_serve: str):
    request = read_request(client_socket)
    response = router(request, directory_to_serve)
    respond(client_socket, response)
    client_socket.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.

    # parse the directory to server from the command line
    # the directoy will be passed by --directory
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="the directory to serve")
    args = parser.parse_args()
    directory = args.directory

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    # use threading to handle multiple requests
    while True:
        client_socket, client_address = server_socket.accept()
        clinet_thread = threading.Thread(target=handle_client, args=(client_socket, directory))
        clinet_thread.daemon = True
        clinet_thread.start()



if __name__ == "__main__":
    main()
