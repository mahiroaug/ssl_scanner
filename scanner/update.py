import mysql.connector
import sys
import os
from ssl_certificate_checker import scan

def updater(domain,subject,issuer,sig_algo,start_date,expiry_date,checkdate):
    cnx = None
    try:
        cnx = mysql.connector.connect(
            user='root',
            password=os.environ['MYSQL_ROOT_PASSWORD'],
            host='DB',
            port='3306',
            db='Certificates',
            charset='utf8'
        )
        
        if cnx.is_connected:
            print("DB connected!")
            
        cursor = cnx.cursor()
        
        ## Before
        sql = ('''
        SELECT *
        FROM Certificates
        WHERE Domain = %s
        ''')
        cursor.execute(sql, (domain,))
        print(cursor.fetchall())
    
        ## date format
        start_date = start_date.date()
        expiry_date = expiry_date.date()
        checkdate = checkdate
      
        ## Update
        sql = ('''
        UPDATE Certificates
        SET Subject = %s, Issuer = %s, SigAlgorithm = %s, Valid_From = %s, Valid_To = %s, Last_Check = %s
        WHERE Domain = %s;
        ''')
        param = (subject,issuer,sig_algo,start_date,expiry_date,checkdate,domain)
        cursor.execute(sql, param)
        cnx.commit()
    
        ## After
        sql = ('''
        SELECT *
        FROM Certificates
        WHERE Domain = %s
        ''')
        cursor.execute(sql, (domain,))
        print(cursor.fetchall())
    
    except Exception as e:
        print(f"Error Occurred: {e}")
        
    finally:
        if cnx is not None and cnx.is_connected():
            cnx.close()


if __name__=="__main__":
    # Check Argument
    if len(sys.argv) != 2:
        print("not match argument")
        sys.exit()

    # URL of the website whose SSL certificate you want to check
    ### print(sys.argv[1])
    url = sys.argv[1]
    subject,issuer,sig_algo,start_date,expiry_date,checkdate = scan(url)
    updater(url,subject,issuer,sig_algo,start_date,expiry_date,checkdate)