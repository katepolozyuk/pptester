import os
import typing

def find_environment_variable(name:str, default:str) -> typing.Any:
    try:
        name = os.environ[name]
    except:
        return default

    return name
