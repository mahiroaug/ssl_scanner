import sys
from db_handler import db_handler
from ssl_certificate_checker import scan

def get_record_count():
    sql = ('''
    SELECT COUNT(*)
    FROM Certificates
    ''')

    count = db_handler(sql,None,False)
    
    if count < 0:
        raise ValueError("The result must be a non-negative integer.")
    
    return(count)


def get_record_chunk(start,end):
    sql = ('''
    SELECT Domain
    FROM Certificates
    WHERE ID >= %s AND ID < %s
    ''')

    chunk = db_handler(sql,(start,end),False)
    
    if not chunk:
        raise ValueError("The result must be include some records")
    
    return(chunk)


def get_list(n,id):
    
    count = get_record_count()
    
    # Divide count into n equal parts
    chunk_size = (count - 1) // n
    remainder = (count - 1) % n

    for id in range(1, n + 1):
        # Calculate the range for the given ID
        if id <= remainder:
            start = chunk_size * id + id
            end = start + chunk_size + 1
        else:
            start = chunk_size * id + remainder + 1
            end = start + chunk_size
            
    chunk = get_record_chunk(start,end)
    return(chunk)


def update(domain,subject,issuer,sig_algo,start_date,expiry_date,checkdate):
    sql = ('''
    UPDATE Certificates
    SET Subject = %s, Issuer = %s, SigAlgorithm = %s, Valid_From = %s, Valid_To = %s, Last_Check = %s
    WHERE Domain = %s;
    ''')
    param = (subject,issuer,sig_algo,start_date,expiry_date,checkdate,domain)
    result = db_handler(sql, param, True)

    return(result)


def main(workers,worker_id):
    list = get_list(workers,worker_id)
    
    for row in list:
        domain = row[0]
        scan_result = scan(domain)
        update(domain,*scan_result)


if __name__=="__main__":
    # Check Argument
    if len(sys.argv) != 3:
        print("not match argument")
        sys.exit()

    workers = sys.argv[1]
    worker_id = sys.argv[2]
    
    main(workers,worker_id)