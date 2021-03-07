import psycopg2
from postgis.psycopg import register
import csv
import os

DATABASE_URL = os.environ['DATABASE_URL']

def readCSV(cursor):
    with open('restaurantes.csv', newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(csv_reader)
        for row in csv_reader:
            insert = 'INSERT INTO restaurant({}) VALUES ({})'
            row2 = ["'" + x + "'" if i not in [1, 9, 10] else x for i, x in enumerate(row)]
            headers2 = headers[:9]
            headers2.append('geog')
            row3 = row2[:9]
            row3.append("'POINT({} {})'".format(row2[10], row2[9]))
            cursor.execute(insert.format(','.join(headers2), ','.join(row3)))
                


if __name__ == '__main__':
    conn = psycopg2.connect(DATABASE_URL, sslmode='require', database='restaurants')
    register(conn)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS restaurant')
    cursor.execute('CREATE TABLE restaurant ( id TEXT PRIMARY KEY, rating INTEGER, name TEXT, site TEXT, email TEXT, phone TEXT, street TEXT, city TEXT, state TEXT, geog geography(point), CHECK (rating BETWEEN 0 AND 4))')
    readCSV(cursor)
    cursor.execute('SELECT * FROM restaurant')
    conn.commit()
    cursor.close()
    conn.close()
