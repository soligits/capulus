import re

format_keys = {
    "register": set(["username", "password"]),
    "login": set(["username", "password"]),
    "logout": set()
}

regex_keys = {
    "username": re.compile(r"^[a-zA-Z0-9_]{3,16}$"),
    "password": re.compile(r"^[a-zA-Z0-9_]{3,16}$")
}


def validate_request_json(request, request_name):
    """
    check if the request has the correct format
    :param request: dict
    :param request_name: str
    :return: bool
    """
    if request_name not in format_keys:
        raise ValueError("Invalid request name")
    if set(request.keys()) != format_keys[request_name]:
        return False
    for key in request.keys():
        if not regex_keys[key].match(request[key]):
            return False
    return True

def validate_value(value, value_name):
    """
    check if the value has the correct format
    :param value: str
    :param value_name: str
    :return: bool
    """
    if value_name not in regex_keys:
        raise ValueError("Invalid value name")
    return regex_keys[value_name].match(value) is not None