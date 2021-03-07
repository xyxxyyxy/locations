from flask import Flask, request, jsonify
import psycopg2
from postgis.psycopg import register
import os
import re

DATABASE_URL = os.environ['DATABASE_URL']

print(DATABASE_URL)
app = Flask(__name__)


def connect():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require', database='restaurants')
    register(conn)
    cursor = conn.cursor()
    return conn, cursor

@app.route("/restaurants/<id>", methods=['GET', 'DELETE'])
def with_id(id):
    if request.method == 'GET':
        conn, cursor = connect()
        query = "SELECT id, rating, name, site, email, phone, street, city, state, ST_AsText(geog) FROM restaurant WHERE id = '{}'"
        cursor.execute(query.format(id))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        if not res:
            return jsonify({"message": "no results found"}), 404
        location= res[9]
        lng = re.search('POINT\((.+?) ', location)
        lat = re.search(' (.+?)\)', location)

        restaurant = {"id": res[0], "rating":res[1], "name":res[2], "site":res[3],
                      "email": res[4], "phone": res[5], "street": res[6],
                      "city": res[7], "state": res[8], "lng": float(lng.group(1)), "lat": float(lat.group(1))}
        return jsonify(restaurant), 200
    if request.method == 'DELETE':
        conn, cursor = connect()
        query = "SELECT id  FROM restaurant WHERE id = '{}'"
        cursor.execute(query.format(id))
        res = cursor.fetchone()
        if not res:
            cursor.close()
            conn.close()
            return jsonify({"message": "no results found"}), 404
        queryDelete = "DELETE FROM restaurant WHERE id = '{}'"
        cursor.execute(queryDelete.format(id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "deleted restaurant successfully"}), 200





@app.route("/restaurants", methods=['GET', 'PUT'])
def without_id():
    if request.method == 'GET':
        sort = request.args.get('sort', "id")
        direction = request.args.get('direction', "asc")
        limit = request.args.get('limit', type=int, default=25)
        page = request.args.get('page', type=int, default=1)
        offset = (page-1)*limit
        direction = direction.upper()
        conn, cursor = connect()
        query = "SELECT id, rating, name, site, email, phone, street, city, state, ST_AsText(geog) FROM restaurant ORDER BY {} {} LIMIT {} OFFSET {}"
        cursor.execute(query.format(sort, direction, limit, offset))
        res= [x for x in cursor]
        queryCount = "SELECT count(*) FROM restaurant"
        cursor.execute(queryCount)
        count = cursor.fetchone()
        cursor
        cursor.close()
        conn.close()
        if not res:
            return jsonify({"message": "no results found"}), 404
        restaurants = []
        for elem in res:
            location= elem[9]
            lng = re.search('POINT\((.+?) ', location)
            lat = re.search(' (.+?)\)', location)
            restaurant = {"id": elem[0], "rating":elem[1], "name":elem[2], "site":elem[3],
                          "email": elem[4], "phone": elem[5], "street": elem[6],
                          "city": elem[7], "state": elem[8], "lng": float(lng.group(1)), "lat": float(lat.group(1))}
            restaurants.append(restaurant)
        return jsonify({"data":restaurants, "total":count[0]}), 200
    if request.method == 'PUT':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        restaurant = {}
        restaurant["id"] = request.json.get('id', None)
        restaurant["rating"] = request.json.get('rating', None)
        restaurant["name"] = request.json.get('name', None)
        restaurant["site"] = request.json.get('site', None)
        restaurant["email"] = request.json.get('email', None)
        restaurant["phone"] = request.json.get('phone', None)
        restaurant["street"] = request.json.get('street', None)
        restaurant["city"] = request.json.get('city', None)
        restaurant["state"] = request.json.get('state', None)
        restaurant["lat"] = request.json.get('lat', None)
        restaurant["lng"] = request.json.get('lng', None)
        for key in restaurant.keys():
            if restaurant[key] == None:
                return jsonify({"message": "{} required".format(key)}),400
            if key not in ["rating", "lng", "lat"]:
                restaurant[key] = "'" + restaurant[key] + "'"
            else:
                if type(restaurant[key]) not in [int, float]:
                    return jsonify({"message": "{} needs to be numeric".format(key)}),400
                restaurant[key] = str(restaurant[key])
        if restaurant["rating"] not in [str(x) for x in range(0,5)]:
            return jsonify({"message": "rating needs to be an integer from 0 to 4"}),400

        restaurant['geog'] = "'POINT({} {})'".format(restaurant["lat"], restaurant["lng"])
        del restaurant["lat"]
        del restaurant["lng"]

        conn, cursor = connect()
        query = "SELECT id  FROM restaurant WHERE id = {}"
        cursor.execute(query.format(restaurant["id"]))
        res = cursor.fetchone()
        if not res:
            insert = 'INSERT INTO restaurant({}) VALUES ({})'
            cursor.execute(insert.format(','.join(restaurant.keys()), ','.join(restaurant.values())))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"message": "inserted succesfully"}), 200
        id = restaurant["id"]
        del restaurant["id"]
        insert = 'UPDATE restaurant SET {} WHERE id = {}'
        to_set = [key + " = " + val for key, val in restaurant.items()]
        cursor.execute(insert.format(' , '.join(to_set), id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "inserted succesfully"}), 200


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
    cursor.execute("SELECT stddev(rating), avg(rating), count(rating) FROM restaurant WHERE ST_DWITHIN(geog ,geography('POINT({} {})'), {})".format(long, lat, radius))
    res = cursor.fetchone()
    std= res[0]
    avg= res[1]
    count= res[2]
    cursor.close()
    conn.close()
    std = std if std else 0
    if count == 0:
        return jsonify({"message": "no results found"}), 404
    return jsonify({"std": round(float(std), 3), "avg": round(float(avg), 3), "count": count}), 200




if __name__ == '__main__':
    app.run(threaded=True, port=5000)