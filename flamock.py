import logging
from argparse import ArgumentParser
from flask_factory import FlaskFactory
from logging_format import logging_format

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

    app = FlaskFactory.flask_factory()

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
    app.response_manager.logs_url = '/%s/logs' % FlaskFactory.admin_path
    app.run(debug=(args.loglevel == logging.DEBUG), host='0.0.0.0', port=args.port, threaded=True)
