import mysql.connector
import docker
import os

cnx = None
client = docker.from_env()

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
        print("connected!")
        
    cursor = cnx.cursor()
    
    sql = ('''
    SELECT ID, Domain, Last_Check
    FROM Certificates 
    ''')
    
    cursor.execute(sql)
    
    
    scanner_base_image = 'ssl-scanner-image'
    
    #ネットワーク名を検索
    network_name_contains = 'mysql_NW'
    network_name = network_name_contains
    for network in client.networks.list():
        if network_name_contains in network.name:
            network_name = network.name
    
    #メイン処理
    for (ID, Domain, Last_Check) in cursor:
        print(f"{ID:02} - {Domain:17} : {Last_Check}")

        doc_name = 'doc_scanner-for-' + Domain
        
        if client.containers.list(filters={"name": doc_name}, all=True):
            # コンテナが存在する場合にのみ、停止と削除を行う
            print("remove container", doc_name)
            container = client.containers.get(doc_name)
            container.stop()
            container.remove()
    
        # container run
        print("start container ", doc_name)
        client.containers.run(
            scanner_base_image,
            Domain,
            name=doc_name,
            network=network_name,
            auto_remove=False,
            detach=True
        ) 
        
except Exception as e:
    print(f"Error Occurred: {e}")
    
finally:
    if cnx is not None and cnx.is_connected():
        cnx.close()

