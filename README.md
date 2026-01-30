# Parley - Command Line TCP/TLS Application Proxy

**Version:** 1.2.0  
**Author:** Garland Glessner  
**License:** GNU General Public License v3.0

---

## Overview

**Parley** is a multi-threaded, modular TCP penetration testing proxy with TLS support. It allows you to intercept, inspect, decode, and modify network traffic between a client and server in real-time.

Designed for penetration testing and security research, Parley supports:
- Plain TCP and TLS connections (both client and server side)
- Modular traffic processing pipelines
- On-the-fly data modification
- Credential extraction from multiple protocols

---

## Usage

```bash
python parley.py --target_host <HOST> [OPTIONS]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--target_host` | Host to connect to (required) |

### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--listen_host` | localhost | Host to listen on |
| `--listen_port` | 8080 | Port to listen on |
| `--target_port` | 80 | Port to connect to |
| `--use_tls_client` | False | Use TLS for client connection |
| `--use_tls_server` | False | Use TLS for server connection |
| `--no_verify` | False | Skip TLS certificate verification (new in v1.2.0) |
| `--certfile` | None | Server SSL certificate for client connection |
| `--keyfile` | None | Server SSL key for client connection |
| `--client_certfile` | None | Client SSL certificate for server connection |
| `--client_keyfile` | None | Client SSL key for server connection |
| `--cipher` | None | Cipher suite to use for TLS |
| `--ssl_version` | None | TLS version (TLSv1, TLSv1.1, TLSv1.2) |

### Examples

**Basic TCP proxy:**
```bash
python parley.py --target_host example.com --target_port 80
```

**TLS proxy with certificate verification:**
```bash
python parley.py --target_host api.example.com --target_port 443 --use_tls_server
```

**TLS proxy skipping certificate verification (self-signed certs):**
```bash
python parley.py --target_host internal.corp --target_port 443 --use_tls_server --no_verify
```

**TLS termination (SSL on client side, plain TCP to server):**
```bash
python parley.py --target_host backend.local --target_port 8080 --use_tls_client --certfile server.crt --keyfile server.key
```

---

## Directory Structure

```
Parley-CLI/
    parley.py                      # Main proxy script
    README.md                      # This file
    module_libs/                   # Shared libraries for modules
        lib3270.py                 # EBCDIC/3270 terminal support
        lib8583.py                 # ISO 8583 payment message parsing
        lib_fix.py                 # FIX financial protocol parsing
        lib_http_basic.py          # HTTP Basic Auth decoding
        lib_jwt.py                 # JWT token decoding
        lib_ldap_bind.py           # LDAP Simple Bind decoding
        lib_smtp_auth.py           # SMTP/IMAP AUTH decoding
        log_utils.py               # Logging utilities
        solace_auth.py             # Solace message broker auth decoding
    modules_client/                # Client-to-server traffic modules
        enabled/                   # Active modules
        disabled/                  # Inactive modules
    modules_server/                # Server-to-client traffic modules
        enabled/                   # Active modules
        disabled/                  # Inactive modules
```

---

## Modules

### Display Modules (Read-Only Inspection)

| Module | Description |
|--------|-------------|
| `Display_Client_Python` / `Display_Server_Python` | Raw Python bytes representation |
| `Display_Client_HEX` / `Display_Server_HEX` | Hex dump with ASCII sidebar |
| `Display_Client_UTF8` / `Display_Server_UTF8` | UTF-8 string display |
| `Display_Client_EBCDIC` / `Display_Server_EBCDIC` | EBCDIC to ASCII (mainframe) |
| `Display_Client_ISO8583` / `Display_Server_ISO8583` | ISO 8583 payment messages |
| `Display_Client_FIX` / `Display_Server_FIX` | FIX financial protocol |
| `Display_Client_JWT` / `Display_Server_JWT` | JWT token decode with expiration |

### Credential Capture Modules

| Module | Protocol | What it Captures |
|--------|----------|------------------|
| `Creds_Client_HTTP_Basic` | HTTP | Basic Auth and Proxy-Auth headers |
| `Creds_Client_SMTP_Auth` | SMTP/IMAP | AUTH PLAIN and AUTH LOGIN |
| `Creds_Client_LDAP_Bind` | LDAP | Simple Bind DN and password |
| `Creds_Client_Solace_Auth` | Solace | Message broker credentials |

### Modification Modules

| Module | Description |
|--------|-------------|
| `0-Modify_Client_HTTP_Headers` | Example HTTP header rewriting |
| `0-Modify_URL` | Example URL modification |

---

## Module Development

Each module must define:

```python
module_description = "Brief description of what this module does"

def module_function(message_num, source_ip, source_port, dest_ip, dest_port, message_data):
    """
    Process a message passing through the proxy.
    
    Args:
        message_num: Sequential message number for this connection
        source_ip: Source IP address
        source_port: Source port number
        dest_ip: Destination IP address
        dest_port: Destination port number
        message_data: The raw message bytes (bytearray)
    
    Returns:
        The message data to forward (can be modified)
    """
    # Process/display/modify message_data
    return message_data
```

To enable a module, move it from `disabled/` to `enabled/`.

---

## Changelog

### v1.2.0
- Added `--no_verify` option to skip TLS certificate verification
- Added FIX protocol decoder modules
- Added JWT token decoder modules
- Added credential capture modules:
  - HTTP Basic Auth
  - SMTP/IMAP AUTH
  - LDAP Simple Bind
- Renamed Solace_Auth_Decode to Creds_Client_Solace_Auth

### v1.1
- Initial public release
- Multi-threaded TCP/TLS proxy
- Modular client and server traffic processing

---

## Contact

Garland Glessner  
Email: gglessner@gmail.com
