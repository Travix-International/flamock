import logging
from flask import Flask
from flask import request
from argparse import ArgumentParser
from response_manager import ResponseManager
from expectation_manager import ExpectationManager
from custom_reponse import CustomResponse
from json_logging import JsonLogging

logging_format = '%(message)s'
admin_path = 'flamock'


app = Flask(__name__)
with app.app_context():
    app.json_logger = JsonLogging(app.logger)


@app.route('/%s/remove_all_expectations' % admin_path, methods=['POST'])
def admin_remove_all_expectations():
    app.json_logger.info("Remove all expectations")
    return ExpectationManager.remove_all().to_flask_response()


@app.route('/%s/remove_expectation' % admin_path, methods=['POST'])
def admin_remove_expectation():
    request_data = request.data.decode()
    app.json_logger.info("Remove expectation: %s" % CustomResponse.remove_linebreaks(request_data))
    req_data_dict, resp = ExpectationManager.json_to_dict(request_data)
    if req_data_dict is None and resp.staus_code != 200:
        return resp.to_flask_response()

    return ExpectationManager.remove(req_data_dict).to_flask_response()


@app.route('/%s/get_expectations' % admin_path, methods=['POST'])
def admin_get_expectations():
    app.json_logger.info("Get expectations")
    return ExpectationManager.get_expectations_as_response().to_flask_response()


@app.route('/%s/add_expectation' % admin_path, methods=['POST'])
def admin_add_expectation():
    request_data = request.data.decode()
    app.json_logger.info("Add expectation: %s" % CustomResponse.remove_linebreaks(request_data))
    req_data_dict, resp = ExpectationManager.json_to_dict(request_data)
    if req_data_dict is None and resp.status_code != 200:
        return resp.to_flask_response()

    return ExpectationManager.add(req_data_dict).to_flask_response()


@app.route('/%s/logs' % admin_path, defaults={'id': ''}, methods=['GET'])
@app.route('/%s/logs/<path:id>' % admin_path, methods=['GET'])
def admin_logs(id):
    return ResponseManager.return_logged_messages(id).to_flask_response()


@app.route('/%s/status' % admin_path, methods=['GET'])
def admin_status():
    return ExpectationManager.status().to_flask_response()


@app.route('/', defaults={'request_path': ''}, methods=['GET', 'POST'])
@app.route('/<path:request_path>', methods=['GET', 'POST'])
def mock_process(request_path):
    query_string = request.query_string.decode()
    path = request.full_path[1:]  # copy full path without first slash
    if len(query_string) == 0:
        path = path[:len(path)-1]  # remove question char in the end if query is empty
    req = {'method': request.method,
           'path': path,
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

    argument_parser.add_argument("-phd", "--proxy_headers",
                                 type=str,
                                 default=None,
                                 action="store",
                                 required=False,
                                 help="Headers to add when proxing in format header1=value1;header2=value2")

    argument_parser.add_argument("-wl", "--whitelist",
                                 type=str,
                                 default="travix.com",
                                 action="store",
                                 required=False,
                                 help="Whitelist of hosts. A list in format host1,host2...")

    argument_parser.add_argument("-p", "--port",
                                 type=int,
                                 default=1080,
                                 action="store",
                                 required=False,
                                 help="flamock port for incoming requests")

    argument_parser.add_argument("-e", "--expectations",
                                 type=str,
                                 default=None,
                                 action="store",
                                 required=False,
                                 help="Expectations to be loaded to flamock at startup. JSON format")

    args = argument_parser.parse_args()

    logging.basicConfig(format=logging_format)
    if args.loglevel == logging.INFO:
        # disable werkzeug logs for INFO level
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger().setLevel(args.loglevel)

    if args.proxy_host is not None:
        scheme = args.proxy_scheme
        expectation = {
            'key': 'fwd',
            'forward':
                {
                    'scheme': scheme,
                    'host': args.proxy_host
                },
            'priority': 0
        }

        if args.proxy_headers is not None:
            dict_headers = {}
            for pair in args.proxy_headers.split(';'):
                key, value = pair.split('=')
                dict_headers[key] = value
            expectation['forward']['headers'] = dict_headers

        ExpectationManager.add(expectation)

        if args.whitelist is not None:
            ResponseManager.host_whitelist = args.whitelist.split(',')

    if args.expectations is not None:
        expectations, response = ExpectationManager.json_to_dict(args.expectations)
        if response.status_code != 200:
            raise Exception(response.text)
        for expectation in expectations:
            ExpectationManager.add(expectation)
    ResponseManager.logs_url = '/%s/logs' % admin_path
    app.run(debug=(args.loglevel == logging.DEBUG), host='0.0.0.0', port=args.port, threaded=True)
