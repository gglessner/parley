# parley
 Multi-Threaded Modular TCP Penetration Testing Proxy with TLS support

usage: parley.py [-h] [--listen_host LISTEN_HOST] [--listen_port LISTEN_PORT] --target_host TARGET_HOST [--target_port TARGET_PORT] [--use_tls_client]
                 [--use_tls_server] [--certfile CERTFILE] [--keyfile KEYFILE] [--client_certfile CLIENT_CERTFILE] [--client_keyfile CLIENT_KEYFILE] [--cipher CIPHER]
                 [--ssl_version {TLSv1,TLSv1.1,TLSv1.2}]

Multi-Threaded Modular TCP Penetration Testing Proxy with TLS support

optional arguments:
  -h, --help            show this help message and exit
  --listen_host LISTEN_HOST
                        Host to listen on
  --listen_port LISTEN_PORT
                        Port to listen on
  --target_host TARGET_HOST
                        Host to connect to
  --target_port TARGET_PORT
                        Port to connect to
  --use_tls_client      Use TLS for the client connection (default: False)
  --use_tls_server      Use TLS for the connection to the server (default: False)
  --certfile CERTFILE   Path to server SSL certificate file for client connection
  --keyfile KEYFILE     Path to server SSL key file for client connection
  --client_certfile CLIENT_CERTFILE
                        Path to client SSL certificate file for server connection
  --client_keyfile CLIENT_KEYFILE
                        Path to client SSL key file for server connection
  --cipher CIPHER       Cipher suite to use for TLS
  --ssl_version {TLSv1,TLSv1.1,TLSv1.2}
                        SSL/TLS version to use
