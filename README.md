# locations-restaurants

[heroku deployment](https://locations-restaurant.herokuapp.com/restaurants)


## usage:

### GET RESTAURANTS

`GET https://locations-restaurant.herokuapp.com/restaurants`

returns paginated list of restaurants, you can change page and page size along with order by changing parameters:

- ?page=1
- ?limit=25
- ?direction=asc
- ?sort=id

defaults are shown above

### PUT RESTAURANTS

`PUT https://locations-restaurant.herokuapp.com/restaurants`

accepts json object to be put (inserted or updated) into database requiring following fields:

`{
    "id": string,
    "rating": int,
    "name": string,
    "site": string,
    "email": string,
    "phone": string,
    "street: string",
    "city": string,
    "state": string,
    "lat": float,
    "lng": float
}`

### GET RESTAURANTS <ID>

`GET https://locations-restaurant.herokuapp.com/restaurants/<id>`

returns a specific retaurant by its id.

### DELETE RESTAURANTS <ID>

`DELETE https://locations-restaurant.herokuapp.com/restaurants/<id>`

removes a specific retaurant by its id.


### DELETE RESTAURANTS <ID>

`GET https://locations-restaurant.herokuapp.com/restaurants/statistics`

requieres arguments:

- ?longitude
- ?latitude
- ?radius

returns average, standard deviation and count of restaurants in the specified radius of the given coordinates