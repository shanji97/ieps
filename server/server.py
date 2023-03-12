from crawldb_model import *
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask
from flask import jsonify
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
basic_auth = HTTPBasicAuth()

USERNAME = "fri"
PASSWORD = "fri-pass"

session = scoped_session(
    sessionmaker(
        autoflush=True,
        autocommit=False,
        bind=engine
    ))


@basic_auth.verify_password
def verify_password(username, password):
    if password == PASSWORD and username == USERNAME:
        return username
    else:
        return None


@basic_auth.error_handler
def basic_auth_error(status):
    return jsonify({"success": False, "message": "Wrong credentials!"}), status


@app.errorhandler(404)
def not_found_error(_):
    return jsonify({"success": False, "message": "Object not found!"}), 404


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"success": False, "message": "Server error!"}), 500


@app.route('/db/get_counter_values', methods=['GET'])
@basic_auth.login_required
def fl_get_values():
    results = session.query(Counters).all()
    results = [{
        "id": r.counter_id,
        "value": r.value
    } for r in results]
    return jsonify(results)


@app.route('/db/reset_counter_values', methods=['POST'])
@basic_auth.login_required
def fl_restart():
    session.query(Counters).update({'value': 0})
    session.commit()
    return jsonify({"success": True})


@app.route('/db/get_data_types', methods=['GET'])
@basic_auth.login_required
def get_data_types():
    results = session.query(DataType).all()
    return jsonify([d.code for d in results])


if __name__ == "__main__":
    app.run(port=8000)
