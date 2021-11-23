from flask import Flask, jsonify, abort
from flask.globals import request
from flask.wrappers import Response


mock_data = [
    {
        "first_name":"Oleksandr",
        "last_name":"Syrotiuk",
    },
    {
        "first_name":"Kateryna",
        "last_name":"Poloziuk",
    },
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


@app.route("/get_by_param_index/<int:id>")
def get_by_param_id(id:int) -> Response:
    if id > len(mock_data):
        abort(404)

    record = mock_data[id]
    return jsonify(record)


@app.route("/get_by_request_index")
def get_by_body_id() -> Response:
    data = request.get_json(force=True)
    if data is None:
        abort(400)

    id = int(data["id"])
    if id is None:
        abort(400)

    record = mock_data[id]
    return jsonify(record)