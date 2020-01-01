import mysql.connector
mydb=  mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='5SC43HhU5a^t',
    database = "testdb"
)


cur = mydb.cursor()
# cur.execute("CREATE DATABASE testdb")

def get_databases():
    cur.execute("SHOW DATABASES")
    databases = cur.fetchall()
    print(databases)
    return databases

extable='students'
## Make students table
# if table in databases[0]:
cmd = f"DROP TABLE IF EXISTS {table}"
# print(f"Dropping table {table}")
cur.execute(cmd)
    
cmd = f"CREATE TABLE {table} (user_id INTEGER AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))"
cur.execute(cmd)
print('Success!')
# for db in cur:
#     print(db)
