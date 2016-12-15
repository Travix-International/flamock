import logging
from flask import Flask
from flask import request
from argparse import ArgumentParser
from response_manager import ResponseManager
from expectation_manager import ExpectationManager
from custom_reponse import CustomResponse
from json_logging import JsonLogging
from extensions import Extensions

logging_format = '%(message)s'
admin_path = 'flamock'


def flask_factory():
    flask_app = Flask(__name__)
    set_context(flask_app)
    set_routes(flask_app)
    CustomResponse.flask_app = flask_app
    return flask_app


def set_context(flask_app):
    with flask_app.app_context():
        flask_app.json_logger = JsonLogging(flask_app.logger)
        flask_app.expectation_manager = ExpectationManager()
        flask_app.response_manager = ResponseManager(flask_app.expectation_manager)


def set_routes(flask_app):

    @flask_app.route('/%s/remove_all_expectations' % admin_path, methods=['POST'])
    def admin_remove_all_expectations():
        flask_app.json_logger.info("Remove all expectations")
        flask_app.expectation_manager.clear()
        return CustomResponse("All expectations were removed").to_flask_response()

    @flask_app.route('/%s/remove_expectation' % admin_path, methods=['POST'])
    def admin_remove_expectation():
        request_data = request.data.decode()
        flask_app.json_logger.info("Remove expectation: %s" % CustomResponse.remove_linebreaks(request_data))
        req_data_dict, resp = flask_app.expectation_manager.json_to_dict(request_data)
        if req_data_dict is None and resp.staus_code != 200:
            return resp.to_flask_response()

        return flask_app.expectation_manager.remove(req_data_dict).to_flask_response()

    @flask_app.route('/%s/get_expectations' % admin_path, methods=['POST'])
    def admin_get_expectations():
        flask_app.json_logger.info("Get expectations")
        return flask_app.expectation_manager.get_expectations_as_response().to_flask_response()

    @flask_app.route('/%s/add_expectation' % admin_path, methods=['POST'])
    def admin_add_expectation():
        request_data = request.data.decode()
        flask_app.json_logger.info("Add expectation: %s" % CustomResponse.remove_linebreaks(request_data))
        req_data_dict, resp = flask_app.expectation_manager.json_to_dict(request_data)
        if req_data_dict is None and resp.status_code != 200:
            return resp.to_flask_response()

        return flask_app.expectation_manager.add(req_data_dict).to_flask_response()

    @flask_app.route('/%s/logs' % admin_path, defaults={'id': ''}, methods=['GET'])
    @flask_app.route('/%s/logs/<path:id>' % admin_path, methods=['GET'])
    def admin_logs(id):
        return flask_app.response_manager.return_log_messages(id).to_flask_response()

    @flask_app.route('/%s/status' % admin_path, methods=['GET'])
    def admin_status():
        return flask_app.expectation_manager.status().to_flask_response()

    @flask_app.route('/', defaults={'request_path': ''}, methods=['GET', 'POST'])
    @flask_app.route('/<path:request_path>', methods=['GET', 'POST'])
    def mock_process(request_path):
        query_string = request.query_string.decode()
        path = request.full_path[1:]  # copy full path without first slash
        if len(query_string) == 0:
            path = path[:len(path)-1]  # remove question char in the end if query is empty
        req = {'method': request.method,
               'path': path,
               'headers': Extensions.list_of_tuples_to_dict(request.headers),
               'body': request.get_data(True).decode(),
               'cookies': request.cookies}
        return flask_app.response_manager.generate_response(req).to_flask_response()


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

    app = flask_factory()

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

        app.expectation_manager.add(expectation)

        if args.whitelist is not None:
            app.response_manager.host_whitelist = args.whitelist.split(',')

    if args.expectations is not None:
        expectations, response = app.expectation_manager.json_to_dict(args.expectations)
        if response.status_code != 200:
            raise Exception(response.text)
        for expectation in expectations:
            app.expectation_manager.add(expectation)
    app.response_manager.logs_url = '/%s/logs' % admin_path
    app.run(debug=(args.loglevel == logging.DEBUG), host='0.0.0.0', port=args.port, threaded=True)
