import sys
import time
from db_handler import db_handler
from ssl_certificate_checker import scan

def get_record_count():
    sql = ('''
    SELECT COUNT(*)
    FROM Certificates
    ''')

    count_result = db_handler(sql,None,False)[0]
    if isinstance(count_result, tuple):
        #print("tuple")
        count = int(count_result[0])
    elif len(count_result) == 0:
        raise ValueError("No record count returned from database")
    else:
        count = int(count_result)
        
    print("type=",type(count)," value=",count)
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
    sql = ('''
    UPDATE Certificates
    SET Subject = %s, Issuer = %s, SigAlgorithm = %s, Valid_From = %s, Valid_To = %s, Last_Check = %s
    WHERE Domain = %s;
    ''')
    param = (subject,issuer,sig_algo,start_date,expiry_date,checkdate,domain)
    
    print(param)
    result = db_handler(sql, param, True)

    return(result)


def main(workers,worker_id):
    list = get_list(int(workers),int(worker_id))
    
    for row in list:
        domain = row[0]
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
    