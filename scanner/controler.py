import sys
import time
from ssl_certificate_checker import scan
from db import db


def get_record_count():
    with db as tx:
        certificates = tx["Certificates"]
        count = certificates.count()
    print("type=",type(count)," value=",count)
    return(count)


def get_record_chunk(start,end):
    with db as tx:
        certificates = tx["Certificates"]
        # https://dataset.readthedocs.io/en/latest/queries.html#advanced-filters
        entries = certificates.find(ID={'between': (start, end)})
        domains = [entry['Domain'] for entry in entries]
    print(domains)
    return domains


def get_list(n,id):
    
    count = get_record_count()
    
    # Divide count into n equal parts
    S = (count) // n
    m = (count) % n

    if id <= m:
        start = (id - 1) * (S + 1) + 1
        end = id * (S + 1)

        if id == 1:
            start = 1

    else:
        start = (id - 1) * S + 1 + m
        end = id * S + m
        
    print("start=",start,",end=",end)   
     
    chunk = get_record_chunk(start,end)
    print("chunk=")
    print(chunk)
    return(chunk)


def update(domain,subject,issuer,sig_algo,start_date,expiry_date,checkdate):
    data = dict(
        Domain=domain,
        Subject=subject,
        Issuer=issuer,
        SigAlgorithm=sig_algo,
        Valid_From=start_date,
        Valid_To=expiry_date,
        Last_Check=checkdate,
    )
    with db as tx:
        certificates = tx["Certificates"]
        certificates.update(data, ["Domain"])
    return data


def main(workers,worker_id):
    list = get_list(int(workers),int(worker_id))
    
    for row in list:
        domain = row
        scan_result = scan(domain)
        
        if scan_result:
            update(domain,*scan_result)
        time.sleep(3)


if __name__=="__main__":
    # Check Argument
    if len(sys.argv) != 3:
        print("not match argument")
        sys.exit(1)
    try:
        a1 = int(sys.argv[1])
        a2 = int(sys.argv[2])
        if a1 <= 0 or a2 <= 0:
            raise ValueError("negative values")
    except ValueError as e:
        print(f"argument error: {e}")
        sys.exit(1) 
    except IndexError:
        print("argument error") 
        sys.exit(1)

    workers = a1
    worker_id = a2
    main(workers,worker_id)
    