import logging
from flask import Flask
from pprint import pformat  # noqa F401


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Application_Handler:

    def __init__(self, application_name=__name__, test_mode=True, verbose='DEBUG',
                 app_debug: bool = False, app_object: Flask = None,
                 *args,
                 **kwargs):
        self.applications_name = application_name
        self.app_debug = app_debug


        '''
        test_mode = True will run the application in test mode, 
                        test webhook and endpoint_dict need to be provided at uptime to "up", 
                        it will send a test webhook through the test client and then exit the application.
        test_mode = False will run the application in production mode and will listen for webhooks from TradingView 
                        and execute trades,
        test_mode = 'live' will run the application in live mode just like test_mode = False but will not place orders 
        '''
        assert test_mode in [True, False, "live"], "test_mode must be True, False or \"live\""
        self.live_test_mode = True if test_mode == 'live' else False  # Will run live but not place orders
        self.test_mode = False if self.live_test_mode else test_mode

        assert verbose in ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'], \
            f"Verbose must be one of the following: INFO, DEBUG, WARNING, ERROR, CRITICAL 🚨 {verbose = }"
        app = Flask(self.applications_name) if app_object is None else app_object
        app.logger.setLevel(logging.getLevelName(verbose))

        formatter = CustomFormatter()
        import sys
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)

        # if this is not called, log will output both original and new format
        app.logger.handlers.clear()
        app.logger.addHandler(handler)

        app.logger.critical("This is a critical component of our success 🚀")
        app.logger.error("Don't mistake this for weakness 🚨")
        app.logger.warning("Crankin' up the heat 🔥")
        app.logger.debug("**cough**")
        app.logger.info("**cough** 🤮")

        # logging.basicConfig(filename='error.log', level=logging.DEBUG) # todo: Not really trying to write to file atm
        app.logger.info("App Initialized 🤭 Down to business 🤑")

        self.app = app

    def pretty_print(self, data, log_level='info'):
        assert log_level.upper() in ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL']

        eval(f'self.app.logger.{log_level.lower()}(pformat({data}))')

        # # if data is a dict, pretty print it else just print it
        # if isinstance(data, dict):
        #     eval(f'self.app.logger.{log_level.lower()}(pformat({data}))')
        # else:
        #     self.app.logger.info(data)

    def add_endpoints(self, endpoint_info_dict):
        """
        e.g.
        endpoints = dict(endpoint_name=dict(
            rule='/endpoint_url',
            function=function_to_run,
            methods=['POST', ... , GET]),
            # ...
        )
        """
        assert isinstance(endpoint_info_dict, dict), "Endpoints must be a dictionary 🚨"
        for endpoint_name, endpoint_info in endpoint_info_dict.items():
            self.app.add_url_rule(endpoint_info['rule'], endpoint_name, endpoint_info['function'],
                                  methods=endpoint_info['methods'])
            self.ensure_endpoint(endpoint_info=endpoint_info)
            self.app.logger.info(f"Added Endpoint {endpoint_name} 🚀")

    def up(self, test_webhook_message=None, test_endpoint_dict=None, ):
        self.app.logger.info(f"Running {self.applications_name}")

        if not self.test_mode:
            # self.app.run(debug=self.app_debug)
            use_reloader = False if self.app_debug else None
            import threading
            # threading.Thread(target=lambda: self.app.run(host=self.host_name, port=self.port, debug=self.app_debug,
            #                                              use_reloader=use_reloader), daemon=True).start()
            self.app.run(host=self.host, port=self.port, debug=self.app_debug,
                         use_reloader=use_reloader)
            self.app.logger.info(f"{self.applications_name} is now listening for webhooks 🚀")
            self.app.logger.info("we live baby 🤖")
            return True

        else:
            try:
                self.app.logger.info("Test Mode Client Init 🤤")
                assert test_webhook_message and test_endpoint_dict, "You must provide both a DEBUG_WEBHOOK_MESSAGE_BUY and an endpoint_dict 🚨"
                self.app.logger.info(
                    f"{self.applications_name} is in Test Mode, use send_test_webhook(test_webhook = {test_webhook_message}) to send a test webhook 🚀")
                assert test_webhook_message, "No Debug Webhook Message was provided 🚨"
                from flask import json
                # from tests.test_webhook import DEBUG_WEBHOOK_MESSAGE_BUY
                self.send_test_json_webhook(test_webhook_message=json.dumps(test_webhook_message),
                                            endpoint_info=test_endpoint_dict)
                self.app.logger.info("Successfully Exited the Test Webhook call 🤤")
                return True
            except Exception as e:
                self.app.logger.error(f"Error in Test Mode Client Init 🚨 {e}")
                return False

    def down(self):
        # todo implement a way to shut down the app, idk if this worked. A solution is to run the app in a separate thread and then kill the thread

        self.app.logger.info(f"Shutting down {self.applications_name} ... removing endpoints 🚀")
        delete_endpoints = [rule.endpoint for rule in self.app.url_map.iter_rules() if rule.endpoint != 'static']
        for endpoint in delete_endpoints:
            self.app.logger.info(f"Deleting Endpoint {endpoint} 🚀")
            self.app.view_functions.pop(endpoint)
        self.app.logger.info(f"Endpoints Deleted 🚀")
        self.app.logger.info(f"Goodbye 🤖")

    def send_test_json_webhook(self, test_webhook_message, endpoint_info):
        assert self.test_mode, "This method is for test_mode or live_test only not available during production🚨"

        # Ensure that the test webhook is a valid json else dump
        from json import JSONDecodeError
        try:
            from json import loads
            loads(test_webhook_message)
        except JSONDecodeError:
            from json import dumps
            test_webhook_message = dumps(test_webhook_message)

        with self.app.test_client() as cl:
            self.app.logger.info(f"Sending Web-hook to {self.applications_name} in Test Mode ⏳")
            assert cl, "Test-Client did initialise properly 🚨"
            assert self.ensure_endpoint(endpoint_info=endpoint_info) == True, "Endpoint is not valid 🚨"
            self.app.logger.info(f"Sending Web-hook to {self.applications_name} in Test Mode 🚀")
            cl.post('/tradingview_webhook_handler', data=test_webhook_message, content_type='application/json')

    def ensure_endpoint(self, endpoint_info: dict):
        """
        e.g.
        endpoint_dict = dict(
            rule='/endpoint_url',
            function=function_to_run,
            methods=['POST', ... , GET]),
            # ...
        )
        """

        # Get a new MapAdapter instance. For testing purpose, an empty string is fine for the server name.
        adapter = self.app.url_map.bind('')

        # in case of endpoint with multiple methods (e.g. GET and POST) we need to check all of them
        self.app.logger.info(f'Ensuring {endpoint_info["rule"] = } is available 🚀')

        for method in endpoint_info['methods']:
            # Get the endpoint for the given rule
            endpoint, values = adapter.match(f'{endpoint_info["rule"]}', method=method)
            self.app.logger.info(f'{endpoint = }')
            self.app.logger.info(f'{values = }')

            # Get the view function for the endpoint
            view_func = self.app.view_functions[endpoint]
            self.app.logger.info(f'{view_func = }')
            assert view_func == endpoint_info[
                "function"], f"Endpoint {endpoint} is not the same as {endpoint_info['function']} 🚨"

            self.app.logger.info(f'Ensured method {method} for {endpoint_info["rule"] = } is available 🚀')

        self.app.logger.info(f'Ensured {endpoint_info["rule"] = } is available 🚀')

        return True
