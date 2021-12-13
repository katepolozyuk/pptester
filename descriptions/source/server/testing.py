import uuid
import requests

from enum import IntEnum
from typing import Any
from datetime import datetime

from werkzeug.exceptions import ExpectationFailed

from .interface import PPTesterInterface
from .validation import validate_pattern, validate_pattern_dict
from utils.convert import convert_to_dict

class PPTesterResults(IntEnum):
    TEST_UNKNOWN = 0
    TEST_FAILED = 1
    TEST_PASSED = 2


class PPTesterCore:
    server:PPTesterInterface
    logfile_path:str

    @classmethod
    def __init__(self, server:PPTesterInterface, logfile_path:str):
        self.server = server
        self.logfile_path = logfile_path
        pass

    @classmethod
    def test_single_method(self, service_description:Any, resource_description:Any, request_description:Any) -> bool:
        guid = str(uuid.uuid4())

        self.__log_test_event(guid, "starting", "test case starting", service_description["name"], resource_description["endpoint"], request_description["method"])
        if not PPTesterCore.__validate_test_request(request_description):
            self.__log_test_event(guid, "failed", "invalid request format", service_description["name"], resource_description["endpoint"], request_description["method"])
            return PPTesterResults.TEST_FAILED

        result = False
        method = request_description["method"]
        endpoint = f'{service_description["url"]}{resource_description["endpoint"]}'
        try:
            if method == "GET":
                result = self.test_method_internal(guid, endpoint, service_description["name"], resource_description, request_description, requests.get)
            elif method == "POST":
                result = self.test_method_internal(guid, endpoint, service_description["name"], resource_description, request_description, requests.post)
            else:
                self.__log_test_event(guid, "aborted", f"{method} is unsupported", service_description["name"], resource_description["endpoint"], request_description["method"])
                return PPTesterResults.TEST_UNKNOWN
        except Exception as e:
            self.__log_test_event(guid, "failed", f"exception at {str(e)}", service_description["name"], resource_description["endpoint"], request_description["method"])
            return PPTesterResults.TEST_FAILED

        return PPTesterResults.TEST_PASSED if result else PPTesterResults.TEST_FAILED

    @classmethod
    def test_multiple_methods(self, service_description:Any, request_body:str, response_description:str) -> bool:
        test_statuses = list()
        for response_description in response_description:
            test_status = self.test_single_method(service_description, request_body, response_description)
            test_statuses.append(test_status)

        return test_statuses

    @classmethod
    def test_method_internal(self, guid:str, endpoint:str, service_name:str, resource_description:Any, request_description:Any, requster:Any) -> bool:
        PPTesterCore.__log_test_event(guid, "running", "test case started", service_name, resource_description["endpoint"], request_description["method"])

        requst_dict = convert_to_dict(request_description["body"])
        response_dict = convert_to_dict(request_description["response_template"])
        try:
            response = requster(endpoint, json=requst_dict)
            response_data = response.json()
        except Exception as e:
            response_data = dict()

        patterns_validation_resuslts = []
        for key, _ in response_dict.items():
            if key == "text":
                pattern_valid = validate_pattern(response_dict, "text", response.text)
            elif key == "status_code":
                pattern_valid = validate_pattern(response_dict, "status_code", response.status_code)
            else:
                pattern_valid = validate_pattern_dict(response_dict, key, response_data)

            patterns_validation_resuslts.append(pattern_valid)
            if not pattern_valid:
                PPTesterCore.__log_test_event(guid, "error", f"pattern for {key} is invalid", service_name, resource_description["endpoint"], request_description["method"])


        if all(patterns_validation_resuslts):
            PPTesterCore.__log_test_event(guid, "success", f"test case succeded", service_name, resource_description["endpoint"], request_description["method"])
            return True
        else:
            PPTesterCore.__log_test_event(guid, "failed", "test case failed", service_name, resource_description["endpoint"], request_description["method"])
            return False

    @classmethod
    def __log_test_event(self, guid:str, status:str, message:str, service_name:str, endpoint:str, method:str) -> None:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(self.logfile_path, "a") as log_fd:
            log_fd.write(f"id:[{guid}] time:[{timestamp}] service:[{service_name}] endpoint:[{endpoint}] method:[{method}] status:[{status}] message:[{message}]\n")

    @staticmethod
    def __validate_test_request(request_description) -> bool:
        if request_description["method"] == "GET":
            return True
        else:
            return len(request_description["body"]) > 0
