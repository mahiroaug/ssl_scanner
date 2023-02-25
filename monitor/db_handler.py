import mysql.connector
import os

def db_handler(sql,param,commit_flag=False):
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

        if not param:
            cursor.execute(sql)
        else:
            cursor.execute(sql,param)
        
        result = cursor.fetchall()
        ##print(result)
        
        if commit_flag:
            cnx.commit()
        
        return result

    except Exception as e:
        print(f"Error Occurred: {e}")
        
    finally:
        if cnx is not None and cnx.is_connected():
            cnx.close()