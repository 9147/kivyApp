import socket
import netifaces

def get_global_ipv6_address():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET6 in addresses:
            for addr in addresses[netifaces.AF_INET6]:
                ipv6_addr = addr['addr']
                # Check for a global unicast address (not starting with fe80:: or fd00::/8)
                if ipv6_addr and not ipv6_addr.startswith('fe80') and not ipv6_addr.startswith('fd'):
                    return ipv6_addr.split('%')[0]  # Remove the zone index if present
    return None

def start_server(ipv6_address, port, stop_event):
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server_socket.bind((ipv6_address, port, 0, 0))
    server_socket.listen(1)
    server_socket.settimeout(1)  # set a timeout of 1 second
    print(f"Server listening on [{ipv6_address}]:{port}")
    while not stop_event.is_set():
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue  # if a timeout occurs, continue the loop to check the stop_event
        print(f"Connected by {addr}")
    
        data = conn.recv(1024)
        print("Received:", data.decode())
    
        response = "Hello from the server!"
        conn.sendall(response.encode())
        conn.close()
    server_socket.close()

def connect_to_server(ipv6_address, port):
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_socket.connect((ipv6_address, port, 0, 0))
    print(f"Connected to server at [{ipv6_address}]:{port}")

    message = "Hello from the client!"
    client_socket.sendall(message.encode())

    data = client_socket.recv(1024)
    print("Received from server:", data.decode())

    client_socket.close()


if __name__ == "__main__":
    ipv6_address = get_global_ipv6_address()
    if ipv6_address:
        port = 1680
        start_server(ipv6_address, port)
    else:
        print("No global IPv6 address found.")
