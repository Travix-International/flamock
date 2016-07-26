import logging
from flask import Flask
from flask import request
from argparse import ArgumentParser
from response_manager import ResponseManager
from expectation_manager import ExpectationManager
from custom_reponse import CustomResponse

logging_format = '[%(asctime)s][%(funcName)s][%(lineno)d][%(levelname)s] %(message)s'
admin_path = 'mock_admin'


app = Flask(__name__)


@app.route('/%s/remove_all_expectations' % admin_path, methods=['POST'])
def admin_remove_all_expectations():
    app.logger.info("-")
    return ExpectationManager.remove_all().to_flask_response()


@app.route('/%s/remove_expectation' % admin_path, methods=['POST'])
def admin_remove_expectation():
    request_data = request.data.decode()
    app.logger.info("Request data: %s" % CustomResponse.remove_linebreaks(request_data))
    req_data_dict, resp = ExpectationManager.json_to_dict(request_data)
    if req_data_dict is None and resp.staus_code != 200:
        return resp.to_flask_response()

    return ExpectationManager.remove(req_data_dict).to_flask_response()


@app.route('/%s/get_expectations' % admin_path, methods=['POST'])
def admin_get_expectations():
    app.logger.info("-")
    return ExpectationManager.get_expectations_as_response().to_flask_response()


@app.route('/%s/add_expectation' % admin_path, methods=['POST'])
def admin_add_expectation():
    request_data = request.data.decode()
    app.logger.info("Request data: %s" % CustomResponse.remove_linebreaks(request_data))
    req_data_dict, resp = ExpectationManager.json_to_dict(request_data)
    if req_data_dict is None and resp.status_code != 200:
        return resp.to_flask_response()

    return ExpectationManager.add(req_data_dict).to_flask_response()


@app.route('/%s/status' % admin_path, methods=['GET'])
def admin_status():
    return ExpectationManager.status().to_flask_response()


@app.route('/', defaults={'request_path': ''}, methods=['GET', 'POST'])
@app.route('/<path:request_path>', methods=['GET', 'POST'])
def mock_process(request_path):
    req = {'method': request.method,
           'path': request_path,
           'headers': ResponseManager.headers_list_to_dict(request.headers),
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

    argument_parser.add_argument("-ps", "--proxy_scheme",
                                 type=str,
                                 default="http",
                                 action="store",
                                 required=False,
                                 help="Schema for proxy")

    argument_parser.add_argument("-ph", "--proxy_host",
                                 type=str,
                                 default=None,
                                 action="store",
                                 required=False,
                                 help="Host for proxy")

    args = argument_parser.parse_args()

    logging.basicConfig(format=logging_format)
    if args.loglevel == logging.INFO:
        # disable werkzeug logs for INFO level
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger().setLevel(args.loglevel)

    if args.proxy_host is not None:
        scheme = args.proxy_scheme
        expectation = {'key': 'fwd', 'forward': {'scheme': scheme, 'host': args.proxy_host}, 'priority': 0}
        ExpectationManager.add(expectation)

    app.run(debug=(args.loglevel == logging.DEBUG), host='0.0.0.0', port=1080, threaded=True)
