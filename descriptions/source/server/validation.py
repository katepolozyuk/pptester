from re import search
from math import isclose
from enum import Enum
from typing import Optional, Any

class token_data:
    type:Any
    additional:int

    def __init__(self, type, match):
        self.type = type
        if match.re.groups > 1:
            self.additional = match.group(2)
        else:
            self.additional = None


def validate_pattern_dict(validation:dict, key:str, target:dict) -> bool:
    if not need_pattern_validation(validation, key):
        return True

    if key not in target:
        return False

    if pattern_is_complex(validation[key]):
        patterns_valid = []
        for key_inner, value in validation[key].items():
            valid = validate_pattern_dict(validation[key], key_inner, target[key])
            patterns_valid.append(valid)
        return all(patterns_valid)

    pattern_data = extract_type_token_data(validation[key])
    if pattern_data is None:
        return False

    typed_value = extract_value(target[key], pattern_data)
    if typed_value is None:
        return False

    if not validate_additional_data(typed_value, pattern_data):
        return False

    return True


def validate_pattern(validation:dict, key:str, target_value:str) -> bool:
    if not need_pattern_validation(validation, key):
        return True

    pattern_data = extract_type_token_data(validation[key])
    if pattern_data is None:
        return False

    typed_value = extract_value(target_value, pattern_data)
    if typed_value is None:
        return False

    if not validate_additional_data(typed_value, pattern_data):
        return False
    return True


def pattern_is_complex(pattern:Any) -> bool:
    if type(pattern) is dict:
        return True
    else:
        return False


def need_pattern_validation(validation:str, key:str) -> bool:
    need_check_pattern = True
    try:
        pattern = validation[key]
        need_check_pattern = pattern != "any"
    except:
        need_check_pattern = False
    return need_check_pattern


def extract_type_token_data(pattern:str) -> token_data:
    result = None
    type_match = search(r"\b(\w+):([0-9].*)?\b", pattern)
    if type_match is None:
        type_match = search(r"\b\w+\b", pattern)

    if type_match:
        if type_match.re.groups > 0:
            type_token = type_match.group(1)
        else:
            type_token = type_match.string

        if type_token == "string":
            result = token_data(str, type_match)
        elif type_token == "int":
            result = token_data(int, type_match)
        elif type_token == "float":
            result = token_data(float, type_match)

    return result


def extract_value(value:str, pattern_data:token_data) -> str:
    try:
        return pattern_data.type(value)
    except ValueError:
        return None


def validate_additional_data(typed_value:Any, pattern_data:token_data) -> bool:
    if not pattern_data.additional:
        return True

    if pattern_data.type == int:
        return typed_value == int(pattern_data.additional)
    elif pattern_data.type == str:
        return len(typed_value) <= int(pattern_data.additional)
    elif pattern_data.type == float:
        return isclose(float(typed_value), float(int(pattern_data.additional)))
    else:
        return False