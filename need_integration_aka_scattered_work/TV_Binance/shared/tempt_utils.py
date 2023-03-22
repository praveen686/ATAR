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
