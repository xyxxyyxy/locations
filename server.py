from flask import Flask, request, jsonify
import psycopg2
from postgis.psycopg import register
import os

DATABASE_URL = os.environ['DATABASE_URL']
app = Flask(__name__)


def connect():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require', database='restaurants')
    register(conn)
    cursor = conn.cursor()
    return conn, cursor

@app.route("/restaurants/statistics", methods=['GET'])
def statistics():
    long = request.args.get('longitude', type=float, default=None)
    lat = request.args.get('latitude', type=float, default=None)
    radius = request.args.get('radius', type=float, default=None)
    if not long:
        return jsonify({"message": "longitude required"}),400
    if not lat:
        return jsonify({"message": "latitude required"}),400
    if not radius:
        return jsonify({"message": "radius required"}),400
    conn, cursor = connect()
    cursor.execute("SELECT stddev(rating), avg(rating), count(rating) FROM restaurant WHERE st_dwithin(geog ,geography('POINT({} {})'), {})".format(long, lat, radius))
    res = cursor.fetchone()
    std= res[0]
    avg= res[1]
    count= res[2]
    cursor.close()
    conn.close()
    std = std if std is not None else 0
    if count == 0:
        return jsonify({"message": "no results found"}), 404
    return jsonify({"std": round(float(std), 3), "avg": round(float(avg), 3), "count": count})




if __name__ == '__main__':
    app.run(host='0.0.0.0')