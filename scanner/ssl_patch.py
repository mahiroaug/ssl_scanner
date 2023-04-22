"""
This code is copied and modified from CPyhon 3.10
https://github.com/python/cpython/blob/v3.10.11/Lib/ssl.py

The LICENSE of this code is available at the following address
https://github.com/python/cpython/blob/v3.10.11/LICENSE

"""

import ssl
import socket


def get_server_certificate_ex(addr: tuple[str, int], ssl_version: int = ssl.PROTOCOL_TLS, timeout=10) -> tuple[str, tuple[str, int]]:
    """Retrieve the certificate from the server at the specified address,
    and return it as a PEM-encoded string.
    If 'ca_certs' is specified, validate the server cert against it.
    If 'ssl_version' is specified, use it in the connection attempt."""
    host, port = addr
    context = ssl._create_unverified_context(ssl_version)
    with socket.create_connection(addr, timeout=timeout) as sock:
        peername = sock.getpeername()
        with context.wrap_socket(sock, server_hostname=host) as sslsock:
            dercert = sslsock.getpeercert(True)
    return ssl.DER_cert_to_PEM_cert(dercert), peername
