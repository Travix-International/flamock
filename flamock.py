import logging
from flask import Flask
from flask import request
from response_manager import ResponseManager
from expectation_manager import ExpectationManager

logging_format = '[%(asctime)s][%(funcName)s][%(lineno)d][%(levelname)s] %(message)s'

app = Flask(__name__)

admin_path = 'flamock'


@app.route('/%s/remove_all_expectations' % admin_path, methods=['POST'])
def admin_remove_all_expectations():
    return ExpectationManager.remove_all().to_flask_response()


@app.route('/%s/remove_expectation' % admin_path, methods=['POST'])
def admin_remove_expectation():
    req_data_dict, resp = ExpectationManager.json_to_dict(request.data.decode())
    if req_data_dict is None and resp.staus_code != 200:
        return resp.to_flask_response()

    return ExpectationManager.remove(req_data_dict).to_flask_response()


@app.route('/%s/get_expectations' % admin_path, methods=['POST'])
def admin_get_expectations():
    return ExpectationManager.get_expectations_as_response().to_flask_response()


@app.route('/%s/add_expectation' % admin_path, methods=['POST'])
def admin_add_expectation():
    req_data_dict, resp = ExpectationManager.json_to_dict(request.data.decode())
    if req_data_dict is None and resp.status_code != 200:
        return resp.to_flask_response()

    return ExpectationManager.add(req_data_dict).to_flask_response()


@app.route('/', defaults={'request_path': ''}, methods=['GET', 'POST'])
@app.route('/<path:request_path>', methods=['GET', 'POST'])
def hello_world(request_path):
    req = {'method': request.method,
           'path': request_path,
           'headers': request.headers,
           'body': request.data.decode(),
           'cookies': request.cookies}
    return ResponseManager.generate_response(req).to_flask_response()


if __name__ == '__main__':
    # logging.basicConfig(filename="flamock.log", level=logging.DEBUG, format=logging_format, filemode='w')

    handler = logging.FileHandler('/home/iryb/flamock/flamock3.log', 'w')
    handler.setFormatter(logging.Formatter(logging_format))
    handler.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)

    app.run(debug=True, host = '0.0.0.0', port=1080 )
