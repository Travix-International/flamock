from flask import Flask
from flask import request
from response_manager import ResponseManager
from expectation_manager import ExpectationManager
from custom_reponse import CustomResponse
from json_logging import JsonLogging
from extensions import Extensions


class FlaskFactory:

    admin_path = 'flamock'

    @classmethod
    def flask_factory(cls):
        flask_app = Flask(__name__)
        cls.__set_context(flask_app)
        cls.__set_routes(flask_app)
        CustomResponse.flask_app = flask_app
        return flask_app

    @classmethod
    def __set_context(cls, flask_app):
        with flask_app.app_context():
            JsonLogging.logger = flask_app.logger
            flask_app.json_logger = JsonLogging
            flask_app.expectation_manager = ExpectationManager()
            flask_app.response_manager = ResponseManager(flask_app.expectation_manager)

    @classmethod
    def __set_routes(cls, flask_app):

        @flask_app.route('/%s/remove_all_expectations' % cls.admin_path, methods=['POST'])
        def admin_remove_all_expectations():
            flask_app.json_logger.info("Remove all expectations")
            flask_app.expectation_manager.clear()
            return CustomResponse("All expectations were removed").to_flask_response()

        @flask_app.route('/%s/remove_expectation' % cls.admin_path, methods=['POST'])
        def admin_remove_expectation():
            request_data = request.data.decode()
            flask_app.json_logger.info("Remove expectation: %s" % CustomResponse.remove_linebreaks(request_data))
            req_data_dict, resp = flask_app.expectation_manager.json_to_dict(request_data)
            if req_data_dict is None and resp.staus_code != 200:
                return resp.to_flask_response()

            return flask_app.expectation_manager.remove(req_data_dict).to_flask_response()

        @flask_app.route('/%s/get_expectations' % cls.admin_path, methods=['POST'])
        def admin_get_expectations():
            flask_app.json_logger.info("Get expectations")
            return flask_app.expectation_manager.get_expectations_as_response().to_flask_response()

        @flask_app.route('/%s/add_expectation' % cls.admin_path, methods=['POST'])
        def admin_add_expectation():
            request_data = request.data.decode()
            flask_app.json_logger.info("Add expectation: %s" % CustomResponse.remove_linebreaks(request_data))
            req_data_dict, resp = flask_app.expectation_manager.json_to_dict(request_data)
            if req_data_dict is None and resp.status_code != 200:
                return resp.to_flask_response()

            return flask_app.expectation_manager.add(req_data_dict).to_flask_response()

        @flask_app.route('/%s/logs' % cls.admin_path, defaults={'id': ''}, methods=['GET'])
        @flask_app.route('/%s/logs/<path:id>' % cls.admin_path, methods=['GET'])
        def admin_logs(id):
            return flask_app.response_manager.return_log_messages(id).to_flask_response()

        @flask_app.route('/%s/status' % cls.admin_path, methods=['GET'])
        def admin_status():
            return flask_app.expectation_manager.status().to_flask_response()

        @flask_app.route('/', defaults={'request_path': ''}, methods=['GET', 'POST'])
        @flask_app.route('/<path:request_path>', methods=['GET', 'POST'])
        def mock_process(request_path):
            query_string = request.query_string.decode()
            path = request.full_path[1:]  # copy full path without first slash
            if len(query_string) == 0:
                path = path[:len(path) - 1]  # remove question char in the end if query is empty
            req = {'method': request.method,
                   'path': path,
                   'headers': Extensions.list_of_tuples_to_dict(request.headers),
                   'body': request.get_data(True).decode(),
                   'cookies': request.cookies}
            return flask_app.response_manager.generate_response(req).to_flask_response()

