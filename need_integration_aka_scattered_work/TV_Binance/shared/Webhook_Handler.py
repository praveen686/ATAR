from pprint import pformat

from flask import request, json


class Webhook_Handler:

    def fetch_new_webhook(self):
        message: dict = self._load_webhook()
        self._clean_webhook(webhook_dict=message, filtered_webhook_config=None)

        assert message, "Webhook message is empty 🚨"

        return message

    # @staticmethod
    # def _load_webhook():
    #     predecoded_data = request.data
    #
    #     if isinstance(predecoded_data, str):
    #         data = predecoded_data.replace("'", '"')
    #     elif isinstance(predecoded_data, bytes):
    #         data = predecoded_data.decode('utf-8').replace("'", '"')
    #     else:
    #         raise Exception(f"Unexpected data type {type(predecoded_data)}")
    #
    #     #
    #     return json.loads(data)

    @staticmethod
    def _load_webhook():
        predecoded_data = request.data
        print(f'predecoded_data: {predecoded_data}')

        if isinstance(predecoded_data, str):
            data = predecoded_data.replace("\'", '\"')
        elif isinstance(predecoded_data, bytes):
            data = predecoded_data.decode().replace("\'", '\"')
        else:
            raise Exception(f"Unexpected data type {type(predecoded_data)}")

        print(f'data: {data}')
        message = json.loads(data)
        print(f'Webhook message: {message}')

        return message

    def _clean_webhook(self, webhook_dict, filtered_webhook_config):  # fixme for the love of god fix this
        # todo filtered_webhook_config = _get_webhook_config(original_webhook_config)
        assert filtered_webhook_config == None, "filtered_webhook_config not implemented yet, please set to None"
        # fixme this is a quick hotfix to work on the rest of the request prior to implementing the filtered_webhook_config
        for section_key in webhook_dict:
            for key, value in webhook_dict[section_key].items():
                self.log.info(f'key: {key}, value: {value}')
                if isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, str):
                            webhook_dict[section_key][key][k] = v.strip()
                        elif v < 0:
                            webhook_dict[section_key][key][k] = None
                elif isinstance(value, str):
                    webhook_dict[section_key][key] = value.strip()
                elif value == None:
                    pass
                elif value < 0:
                    webhook_dict[section_key][key] = None

        print("\n")
        self.log.info(pformat(webhook_dict))
        print("\n")

        return webhook_dict

