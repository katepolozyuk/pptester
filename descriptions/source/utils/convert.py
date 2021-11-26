import json

def convert_to_dict(string:str) -> str:
    if len(string) == 0:
        return dict()

    json_acceptable_string = string.replace("'", "\"")
    json_acceptable_string = json_acceptable_string.replace("\r\n", "")
    try:
        result = json.loads(json_acceptable_string)
        return result
    except Exception as e:
        try:
            result = json.loads(f"{{{json_acceptable_string}}}")
            return result
        except Exception as c:
            return dict()