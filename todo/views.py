import os
import requests
from todo import app

from flask import jsonify, request, url_for
from flask import json

from todo.database import db_session
from todo.models import Entry
from todo.error_handlers import InvalidUsage


@app.before_request
def before_request_func():
    # return os.environ.get("HOSTNAME")
    if os.environ.get("call_downstream", False) == "1":
        downstream = os.environ.get("downstream", "http://todo-downstream:5000")
        verb = request.method
        url = downstream + request.path
        response = requests.request(verb, url=url, headers=request.headers, data=request.data)
        return response.content
        # return requests.get(downstream).content

@app.route("/", methods=["GET", "POST", "DELETE"])
def index():
    if request.method == "POST":
        request_json = request.get_json()
        if "order" in request_json:
            if type(request_json["order"]) is int:
                entry = Entry(request_json["title"], request_json["order"])
            else:
                raise InvalidUsage(str(request_json["order"]) + " is not an integer.")
        else:
            entry = Entry(request_json["title"])
        db_session.add(entry)
        db_session.commit()
        return jsonify(construct_dict(entry))
    else:
        if request.method == "DELETE":
            Entry.query.delete()
            db_session.commit()
        response = []
        for entry in Entry.query.all():
            response.append(construct_dict(entry))
        return json.dumps(response)

@app.route("/<int:entry_id>", methods=["GET", "PATCH", "DELETE"])
def entry(entry_id):
    entry = Entry.query.filter(Entry.id == entry_id).first()
    if request.method == "PATCH":
        request_json = request.get_json()
        if "title" in request_json:
            entry.title = request_json["title"]
        if "completed" in request_json:
            if type(request_json["completed"]) is bool:
                entry.completed = request_json["completed"]
            else:
                raise InvalidUsage(str(request_json["completed"]) + " is not a boolean.")
        if "order" in request_json:
            if type(request_json["order"]) is int:
                entry.order = request_json["order"]
            else:
                raise InvalidUsage(str(request_json["order"]) + " is not an integer.")
        db_session.commit()
    elif request.method == "DELETE":
        db_session.delete(entry)
        db_session.commit()
        return jsonify(dict())
    if entry:
        return jsonify(construct_dict(entry))
    else:
        return jsonify(dict())

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def entry_url(id):
    hostname = os.environ.get("HOSTNAME") 
    return f"http://{hostname}/{id}"

def construct_dict(entry):
    if entry.order:
        return dict(title=entry.title, completed=entry.completed,
            url=entry_url(entry.id),
            order=entry.order)
    else:
        return dict(title=entry.title, completed=entry.completed,
            url=entry_url(entry.id))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
