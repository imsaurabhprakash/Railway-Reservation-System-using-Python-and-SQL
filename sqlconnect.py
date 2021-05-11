import pymysql

#pymysql("hostname","root","password","database name")\
db = pymysql.connect(host = "localhost",user = "root",password = "",database = "rrs")
cursor = db.cursor()

#db.close() is written in the main.py file as we need to close the connection in the end
