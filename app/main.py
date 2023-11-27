# Uncomment this to pass the first stage
import socket


def respond_200(client_socket):
    response = "HTTP/1.1 200 OK\r\n\r\n"
    client_socket.send(response.encode())


def read_request(client_socket):
    buffer_size = 1024
    request = client_socket.recv(buffer_size).decode()
    print(request)
    return request


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    s, _ = server_socket.accept() # wait for client
    read_request(s)
    respond_200(s)



if __name__ == "__main__":
    main()
