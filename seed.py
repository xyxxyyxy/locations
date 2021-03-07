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
            cursor.execute(insert.format(','.join(headers), ','.join(row2)))
                


if __name__ == '__main__':
    conn = psycopg2.connect(DATABASE_URL, sslmode='require', database='restaurants')
    register(conn)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS restaurant ( id TEXT PRIMARY KEY, rating INTEGER, name TEXT, site TEXT, email TEXT, phone TEXT, street TEXT, city TEXT, state TEXT, lat FLOAT, lng FLOAT, CHECK (rating BETWEEN 0 AND 4))')
    readCSV(cursor)
    conn.commit()
    cursor.close()
    conn.close()
