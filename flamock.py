from flask import Flask
from flask import request
from response_manager import ResponseManager
from expectation_manager import ExpectationManager

app = Flask(__name__)

admin_path = 'flamock'


@app.route('/%s/remove_all_expectations' % admin_path)
def admin_remove_all_expectations():
    return ExpectationManager.remove_all().to_flask_response()


@app.route('/%s/remove_expectation' % admin_path)
def admin_remove_expectation():
    return ExpectationManager.remove(request.data).to_flask_response()


@app.route('/%s/get_expectations' % admin_path)
def admin_get_expectations():
    return ExpectationManager.get_expectations_as_response().to_flask_response()


@app.route('/%s/add_expectation' % admin_path)
def admin_add_expectation():
    return ExpectationManager.add(request.data).to_flask_response()


@app.route('/', defaults={'request_path': ''})
@app.route('/<path:request_path>')
def hello_world(request_path):
    req = {'path': request_path, 'headers': request.headers, 'body': request.data, 'cookies': request.cookies}
    return ResponseManager(req).generate().to_flask_response()


if __name__ == '__main__':
    app.run()
