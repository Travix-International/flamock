import logging
from flask import Flask
from flask import request
from argparse import ArgumentParser
from response_manager import ResponseManager
from expectation_manager import ExpectationManager

logging_format = '[%(asctime)s][%(funcName)s][%(lineno)d][%(levelname)s] %(message)s'
admin_path = 'flamock'


app = Flask(__name__)


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

    argument_parser = ArgumentParser(description='Flamock')

    argument_parser.add_argument("-ll", "--loglevel",
                                 type=int,
                                 default=logging.INFO,
                                 action="store",
                                 required=False,
                                 help="Log level 0-50. DEBUG = 10 , INFO = 20, CRITICAL = 50")

    args = argument_parser.parse_args()
    logging.basicConfig(level=args.loglevel, format=logging_format)

    app.run(debug=(args.loglevel == logging.DEBUG), host='0.0.0.0', port=1080)
