from flask import Flask, jsonify, abort
from flask.globals import request
from flask.wrappers import Response
from requests import status_codes


mock_data = [
    {
        "id":0,
        "data": {
            "first_name":"Oleksandr",
            "last_name":"Syrotiuk",
        },
    },
    {
        "id":1,
        "data": {
            "first_name":"Kateryna",
            "last_name":"Poloziuk",
        },
    }
]


app = Flask(__name__)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6500)

# ================================================== SERVICE ROUTES ==========================================
@app.route("/")
def empty_index() -> Response:
    return "Hello, World!"


@app.route("/index")
def real_index() -> Response:
    return "Hello, Index!"


@app.route("/data_access_endpoint", methods=("POST", "GET"))
def data_endpoint() -> Response:
    data = request.get_json(force=True)
    if data is None:
        abort(400)

    if request.method == "GET":
        return get_data(data)
    elif request.method == "POST":
        return insert_data(data)


def get_data(data) -> Response:
    id = int(data["id"])
    if id is None:
        abort(400)

    record = next((item for item in mock_data if item['id'] == id), None)
    return jsonify(record["data"])


def insert_data(data) -> Response:
    if not ("first_name" in data) or not("last_name" in data):
        abort(400)

    new_id = len(mock_data)
    first_name = data["first_name"]
    last_name = data["last_name"]

    new_dict = { "id":new_id, "data": { "first_name":first_name, "last_name":last_name } }
    mock_data.append(new_dict)
    record = next((item for item in mock_data if item["id"] == new_id), None)
    if record is None:
        abort(400)

    return jsonify(record)