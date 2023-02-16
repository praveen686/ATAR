import json

import redis


def ensure_bool(var, exception_values=None):
    if isinstance(var, bool):
        return var
    elif isinstance(var, str):
        if var.lower() == "true":
            return True
        elif var.lower() == "false":
            return False
        else:
            raise Exception(f"str var is {var}")
    elif isinstance(var, int):
        if var == 1:
            return True
        elif var == 0:
            return False
        else:
            raise Exception(f"int var is {var}")
    elif exception_values and var in exception_values:
        return var
    else:
        raise Exception(f"var is {var} of type {type(var)}")


def _pubish_to_multiple_channels(r: redis.Redis, channel_names, message):
    pipe = r.pipeline()  # creates a pipeline object that can be used to execute multiple commands in a single call to the server
    # Publish messages to multiple channels
    for channel_name in channel_names:
        pipe.publish(channel_name, json.dumps(message))
    oks = pipe.execute()
    for ok in oks:
        try:
            assert ok
            print(f"Published to channel {channel_names} --> {message}")
        except Exception as e:
            print(f"Error publishing to channel {channel_name}: {e}")
