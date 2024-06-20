import socket
import netifaces
import json

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
        received_data=json.loads(data.decode('utf-8'))
        print("Received:", received_data)
    
        response = {"message":"Hello from the server!"}
        response=json.dumps(response)
        conn.sendall(response.encode('utf-8'))
        conn.close()
    server_socket.close()

def connect_to_server(ipv6_address, port,message_dict):
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_socket.connect((ipv6_address, port, 0, 0))
    print(f"Connected to server at [{ipv6_address}]:{port}")

    message = json.dumps(message_dict)
    client_socket.sendall(message.encode('utf-8'))

    data = client_socket.recv(1024)
    received_data=json.loads(data.decode('utf-8'))
    print("Received from server:", received_data)

    client_socket.close()


if __name__ == "__main__":
    ipv6_address = get_global_ipv6_address()
    if ipv6_address:
        port = 1680
        start_server(ipv6_address, port)
    else:
        print("No global IPv6 address found.")