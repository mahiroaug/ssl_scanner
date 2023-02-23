from datetime import datetime
import ssl
import OpenSSL
import sys
from cryptography import x509
### from cryptography.hazmat.backends import default_backend

def scan(url):
    cert_data = ssl.get_server_certificate((url,443),ssl_version=ssl.PROTOCOL_SSLv23)

    # Convert to human-readable form
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_data)

    #Subject
    subject = x509.get_subject().commonName
    print('Subject:  ', subject)

    # Validity period start
    start_date_str = x509.get_notBefore().decode()
    start_date = datetime.strptime(start_date_str, '%Y%m%d%H%M%SZ')
    print('notBefore:', start_date, ' (', start_date_str, ')')

    # Validity period end
    end_date_str = x509.get_notAfter().decode()
    expiry_date = datetime.strptime(end_date_str, '%Y%m%d%H%M%SZ')
    print('notAfter: ', expiry_date, ' (', end_date_str, ')')

    # Issuer
    issuer = x509.get_issuer().commonName
    print('Issuer:   ', issuer)

    # Signature Algorithm
    sig_algo = x509.get_signature_algorithm().decode()
    print('Algorithm:', sig_algo)

    # Other information
    ### components = x509.get_subject().get_components()
    ### for component in components:
    ###    print(component)

    now = datetime.now()
    checkdate = now.replace(microsecond=0)
    print('Checkdate:', checkdate)

    return(subject,issuer,sig_algo,start_date,expiry_date,checkdate)


if __name__=="__main__":
    # Check Argument
    if len(sys.argv) != 2:
        print("not match argument")
        sys.exit()

    # URL of the website whose SSL certificate you want to check
    ### print(sys.argv[1])
    url = sys.argv[1]
    scan(url)