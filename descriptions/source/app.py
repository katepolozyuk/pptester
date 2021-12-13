from flask import Flask, abort, redirect, render_template, request, url_for
from flask.wrappers import Response

from server.interface import PPTesterInterface
from server.testing import PPTesterCore

from utils.environment import find_environment_variable
from utils.route import find_directory_path, find_working_directory

import threading

# ================================================== APP =====================================================
working_directory = find_working_directory()
print(f"[PPTester Report System] Working directory deducted do : {working_directory}")

template_directory = find_directory_path([working_directory, f"{working_directory}/../"], "templates")
print(f"[PPTester Report System] Template directory deducted oo : {template_directory}")

pptester_remote_db = find_environment_variable("PPTESTER_DATABATE_REMOTE", "False") == "True"
pptester_logfile = find_environment_variable("PPTESTER_LOG_FILE", "data/output.log")

server = PPTesterInterface(working_directory, remote_db=pptester_remote_db)
tester = PPTesterCore(server, logfile_path=pptester_logfile)

app = Flask(__name__, template_folder=template_directory)
app.secret_key = "development_secret_key"


# ================================================== SERVICE ROUTES ==========================================
@app.route("/")
def index() -> Response:
    service_records = server.service_dao.get_service_records()
    return render_template("index.html", services=service_records)


@app.route("/service/create", methods=("GET", "POST"))
def create_service() -> Response:
    if request.method == "POST":
        name = request.form["name"]
        url = request.form["url"]
        description = request.form["description"]
        if not (name and description and url):
            return render_template("service/create.html")
        else:
            server.service_dao.add_service_record(name, description, url)
            return redirect(url_for("index"))
    elif request.method == "GET":
        return render_template("service/create.html")


@app.route("/service/<int:service_id>")
def show_service(service_id:int) -> Response:
    service_record = server.service_dao.get_service_record(service_id)
    if service_record is None:
        abort(404)

    resource_records = server.resource_dao.get_resource_records(service_id)
    return render_template("service/service.html", service=service_record, resources=resource_records)


@app.route("/service/<int:service_id>/edit", methods=("GET", "POST"))
def edit_service(service_id:int) -> Response:
    service_record = server.service_dao.get_service_record(service_id)
    if service_record is None:
        return redirect(url_for("create_service"))

    if request.method == 'POST':
        name = request.form["name"]
        url = request.form["url"]
        description = request.form["description"]
        server.service_dao.update_service_record(service_id, name, description, url)
        return redirect(url_for("index"))

    return render_template('service/edit.html', service=service_record)


@app.route("/service/<int:service_id>/delete", methods=("POST", ))
def delete_service(service_id:int) -> Response:
    service_record = server.service_dao.get_service_record(service_id)
    if service_record is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        server.service_dao.delete_service_record(service_id)

    return redirect(url_for("index"))


# ================================================== RECORDS ROUTES ==========================================
@app.route("/service/<int:service_id>/resource/<int:resource_id>")
def show_resource_description(service_id:int, resource_id:int) -> Response:
    service_record = server.service_dao.get_service_record(service_id)
    resource_record = server.resource_dao.get_resource_record(service_id, resource_id)
    request_records = server.request_dao.get_request_records(resource_id)
    return render_template("resource/resource.html", service=service_record, resource=resource_record, request_records=request_records)


@app.route("/service/<int:service_id>/resource/create", methods=("GET", "POST"))
def create_resource_description(service_id:int) -> Response:
    if request.method == "POST":
        endpoint = request.form["endpoint"]
        server.resource_dao.add_resource_record(service_id, endpoint)
        return redirect(url_for("show_service", service_id=service_id))

    service_record = server.service_dao.get_service_record(service_id)
    return render_template("resource/create.html", service=service_record)


@app.route("/service/<int:service_id>/resource/<int:resource_id>/edit", methods=("GET", "POST"))
def edit_resource_description(service_id:int, resource_id:int) -> Response:
    if request.method == "POST":
        endpoint = request.form["endpoint"]
        server.resource_dao.update_resource_record(service_id, resource_id, endpoint)
        return redirect(url_for("show_service", service_id=service_id))
    elif request.method == "GET":
        service_record = server.service_dao.get_service_record(service_id)
        if service_record is None:
            return redirect(url_for("create_service"))

        resource_record = server.resource_dao.get_resource_record(service_id, resource_id)
        if resource_record is None:
            return redirect(url_for("create_resource_description", service_id=service_id))

        return render_template("resource/edit.html", service=service_record, resource=resource_record)


@app.route("/service/<int:service_id>/resource/<int:resource_id>/delete", methods=("POST", ))
def delete_resource_description(service_id:int, resource_id:int) -> Response:
    resource_record = server.resource_dao.get_resource_record(service_id, resource_id)
    if resource_record is not None:
        server.resource_dao.delete_resource_record(service_id, resource_id)

    return redirect(url_for("show_service", service_id=service_id))


# ================================================== REQUEST ROUTES ==========================================
@app.route("/service/<int:service_id>/resource/<int:resource_id>/request/create", methods=("GET", "POST"))
def create_request_description(service_id:int, resource_id:int) -> Response:
    service_record = server.service_dao.get_service_record(service_id)
    resource_record = server.resource_dao.get_resource_record(service_id, resource_id)
    if request.method == "POST":
        method = request.form["method"]
        body = request.form["body"]
        response_template = request.form["response_template"]
        server.request_dao.add_request_record(resource_id, method, body, response_template)
        return redirect(url_for("show_resource_description", service_id=service_id, resource_id=resource_id))

    return render_template("request/create.html", service=service_record, resource=resource_record)


@app.route("/service/<int:service_id>/resource/<int:resource_id>/request/<int:request_id>/edit", methods=("GET", "POST"))
def edit_request_description(service_id:int, resource_id:int, request_id:int) -> Response:
    if request.method == "POST":
        method = request.form["method"]
        body = request.form["body"]
        response_template = request.form["response_template"]
        server.request_dao.update_request_record(resource_id, request_id, method, body, response_template)
        return redirect(url_for("show_resource_description", service_id=service_id, resource_id=resource_id))
    elif request.method == "GET":
        service_record = server.service_dao.get_service_record(service_id)
        if service_record is None:
            return redirect(url_for("create_service"))

        resource_record = server.resource_dao.get_resource_record(service_id, resource_id)
        if resource_record is None:
            return redirect(url_for("create_resource_description", service_id=service_id))

        request_record = server.request_dao.get_request_record(resource_id, request_id)
        if request_record is None:
            return redirect(url_for("create_request_description", service_id=service_id, resource_id=resource_id))

        return render_template("request/edit.html", service=service_record, resource=resource_record, request_record=request_record)


@app.route("/service/<int:service_id>/resource/<int:resource_id>/request/<int:request_id>/delete", methods=("POST",))
def delete_request_description(service_id:int, resource_id:int, request_id:int) -> Response:
    request_record = server.request_dao.get_request_record(resource_id, request_id)
    if request_record is not None:
        server.request_dao.delete_request_record(resource_id, request_id)

    return redirect(url_for("show_resource_description", service_id=service_id, resource_id=resource_id))


# ================================================== TESTING ROUTES ==========================================
@app.route("/service/<int:service_id>/resource/<int:resource_id>/test")
def test_resource_by_descriptions(service_id:int, resource_id:int) -> Response:
    service_record = server.service_dao.get_service_record(service_id)
    resource_record = server.resource_dao.get_resource_record(service_id, resource_id)
    request_records = server.request_dao.get_request_records(resource_id)

    def test_function(tester_service, server, service_record, resource_record, request_records):
        new_test_statuses = tester_service.test_multiple_methods(service_record, resource_record, request_records)
        for new_test_status, request_record in zip(new_test_statuses, request_records):
            if (request_record["test_status"] != new_test_status):
                server.request_dao.update_request_record_test_status(resource_id, request_record.id, new_test_status)

    def cycled_range(tester_service, server, service_record, resource_record, request_records):
        for i in range(0, 45000):
            test_function(tester_service, server, service_record, resource_record, request_records)

    def test_mt(server, service_record, resource_record, request_records):
        threads = [threading.Thread(target=cycled_range, args=(tester, server, service_record, resource_record, request_records)) for i in range(0, 4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    test_mt(server, service_record, resource_record, request_records)
    return redirect(url_for("show_resource_description", service_id=service_id, resource_id=resource_id))


@app.route("/service/<int:service_id>/resource/<int:resource_id>/request/<int:request_id>/test")
def test_request_by_description(service_id:int, resource_id:int, request_id:int) -> Response:
    service_record = server.service_dao.get_service_record(service_id)
    resource_record = server.resource_dao.get_resource_record(service_id, resource_id)
    request_record = server.request_dao.get_request_record(resource_id, request_id)

    new_test_status = tester.test_single_method(service_record, resource_record, request_record)
    if (request_record["test_status"] != new_test_status):
        server.request_dao.update_request_record_test_status(resource_id, request_id, new_test_status)

    return redirect(url_for("show_resource_description", service_id=service_id, resource_id=resource_id))



