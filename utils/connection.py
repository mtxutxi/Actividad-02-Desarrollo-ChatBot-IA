import pymssql

conn = pymssql.connect(
    server='A407PC11:1433',
    user='sa',
    password='tiger',
    database='Pubs'
)

cursor = conn.cursor()
cursor.execute('SELECT * FROM titles')
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()