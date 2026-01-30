#!/usr/bin/env python3

# Parley
# Multi-Threaded Modular TCP Penetration Testing Proxy with TLS support
# Copyright Garland Glessner (2025)
# Contact email: gglessner@gmail.com

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ------------------------------------------------------------------------------------------------------------------
# Thank you to Jay Smith - email: CadmusOfThebes@protonmail.com for inspiring me to release this tool to the public.
# ------------------------------------------------------------------------------------------------------------------

import os
import importlib.util
import socket
import ssl
import sys
import argparse
import threading
import select

VERSION = "1.2.0"
TAGLINE = "Multi-Threaded Modular TCP Penetration Testing Proxy with TLS support"

# Construct the path to module_libs in an OS-agnostic way
module_libs_path = os.path.join(os.path.dirname(__file__), 'module_libs')

# Add the path to sys.path if it's not already there
if module_libs_path not in sys.path:
    sys.path.insert(0, module_libs_path)

def handle_client(client_socket, target_host, target_port, use_tls_client, use_tls_server, certfile, keyfile, cipher, ssl_version, client_certfile, client_keyfile, no_verify=False):
    # Create a new socket for forwarding
    forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward_socket.connect((target_host, target_port))
    
    # Get the client and server addresses
    client_ip, client_port = client_socket.getpeername()
    server_ip, server_port = forward_socket.getpeername()
    
    print(f"[+] Connected to server: {client_ip}:{client_port} -> {server_ip}:{server_port}")

    if use_tls_server:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if no_verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        if client_certfile and client_keyfile:
            context.load_cert_chain(certfile=client_certfile, keyfile=client_keyfile)
        if cipher:
            context.set_ciphers(cipher)
        if ssl_version:
            context.options |= {
                'TLSv1': ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_SSLv2,
                'TLSv1.1': ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_SSLv2,
                'TLSv1.2': ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_SSLv3 | ssl.OP_NO_SSLv2,
            }[ssl_version]
        forward_socket = context.wrap_socket(forward_socket, server_hostname=target_host)

    if use_tls_client:
        client_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        if certfile and keyfile:
            client_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        client_socket = client_context.wrap_socket(client_socket, server_side=True)

    sockets = [client_socket, forward_socket]
    buffer_size = 4096  # Buffer size for receiving data
    client_msg_num = 0
    server_msg_num = 0
    
    try:
        while sockets:
            readable, writable, errored = select.select(sockets, [], [])
            for s in readable:
                full_data = bytearray()
                while True:
                    # Read data in chunks
                    data = s.recv(buffer_size)
                    if not data:  # No more data to read
                        break
                    full_data.extend(data)
                    
                    # If we've read less than the buffer size, it means we've read all available data
                    if len(data) < buffer_size:
                        break
                
                if full_data:
                    if s is client_socket:
                        client_msg_num = client_msg_num + 1
                        for module_name, module in loaded_modules_client.items():
                            full_data = module.module_function(client_msg_num, client_ip, client_port, server_ip, server_port, full_data)
                        forward_socket.sendall(full_data)
                    else:
                        server_msg_num = server_msg_num + 1
                        for module_name, module in loaded_modules_server.items():
                            full_data = module.module_function(server_msg_num, server_ip, server_port, client_ip, client_port, full_data)
                        client_socket.sendall(full_data)
                else:
                    # If no data, the socket has closed
                    sockets.remove(s)
                    s.close()
                    if len(sockets) == 0:
                        break  # Both sockets closed, connection ended
    except OSError as e:
        if e.errno == 9:  # Errno 9 is "Bad file descriptor"
            print(f"[-] Connection broken: {client_ip}:{client_port} -> {server_ip}:{server_port}")
        elif e.errno == 54:  # Errno 54 is "Connection reset by peer"
            print(f"[-] Disconnected from server: {client_ip}:{client_port} -> {server_ip}:{server_port}")
        else:
            print(f"Error in connection: {e}")
    except Exception as e:
        print(f"Error in connection: {e}")
    finally:
        for sock in sockets:
            sock.close()

def start_proxy(listen_host, listen_port, target_host, target_port, use_tls_client, use_tls_server, certfile, keyfile, client_certfile, client_keyfile, cipher, ssl_version, no_verify=False):
    # Create a socket to listen on
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((listen_host, listen_port))
    server_socket.listen(5)
    
    print(f"[+] Listening on: {listen_host}:{listen_port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_ip, client_port = client_socket.getpeername()
        print(f"[+] New server socket thread started for {client_ip}:{client_port}")
        # Start a new thread for each client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket, target_host, target_port, use_tls_client, use_tls_server, certfile, keyfile, cipher, ssl_version, client_certfile, client_keyfile, no_verify))
        client_thread.start()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=TAGLINE)
    parser.add_argument('--listen_host', default='localhost', help='Host to listen on')
    parser.add_argument('--listen_port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--target_host', required=True, help='Host to connect to')
    parser.add_argument('--target_port', type=int, default=80, help='Port to connect to')
    parser.add_argument('--use_tls_client', action='store_true', help='Use TLS for the client connection (default: False)')
    parser.add_argument('--use_tls_server', action='store_true', help='Use TLS for the connection to the server (default: False)')
    parser.add_argument('--certfile', help='Path to server SSL certificate file for client connection')
    parser.add_argument('--keyfile', help='Path to server SSL key file for client connection')
    parser.add_argument('--client_certfile', help='Path to client SSL certificate file for server connection')
    parser.add_argument('--client_keyfile', help='Path to client SSL key file for server connection')
    parser.add_argument('--cipher', help='Cipher suite to use for TLS')
    parser.add_argument('--ssl_version', choices=['TLSv1', 'TLSv1.1', 'TLSv1.2'], help='SSL/TLS version to use')
    parser.add_argument('--no_verify', action='store_true', help='Skip TLS certificate verification for server connection (default: False)')

    args = parser.parse_args()

    # Set defaults for TLS to be disabled if not specified
    use_tls_client = args.use_tls_client if args.use_tls_client is not None else False 
    use_tls_server = args.use_tls_server if args.use_tls_server is not None else False 

    print(f"\n[+] Parley v{VERSION} - {TAGLINE}")

    # Define directories using os.path.join for OS agnosticism
    modules_client_dir = os.path.join("modules_client", "enabled")
    modules_server_dir = os.path.join("modules_server", "enabled")

    loaded_modules_client = {}
    loaded_modules_server = {}

    # Load modules_client - Process data received by the client for the server
    print("[+] Loading Client Modules...")
    for filename in sorted(os.listdir(modules_client_dir)):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]

            module_path = os.path.join(modules_client_dir, filename)

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            loaded_modules_client[module_name] = module

            print(f"\t<-> {module_name} - {module.module_description}")

    # Load modules_server - Process data received by the server for the client
    print("[+] Loading Server Modules...")
    for filename in sorted(os.listdir(modules_server_dir)):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]

            module_path = os.path.join(modules_server_dir, filename)

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            loaded_modules_server[module_name] = module

            print(f"\t<-> {module_name} - {module.module_description}")

    start_proxy(args.listen_host, args.listen_port, args.target_host, args.target_port,
                use_tls_client, use_tls_server, args.certfile, args.keyfile, args.client_certfile, args.client_keyfile,
                args.cipher, args.ssl_version, args.no_verify)
