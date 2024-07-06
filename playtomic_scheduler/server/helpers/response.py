from typing import Any
from flask import jsonify


class ResponseHelper:
    @staticmethod
    def parse_response(status_code: int, result: Any):
        """
        Parse response to JSON.

        Args:
        - status_code (int): HTTP status code.
        - result (Any): Response data.
        """
        return jsonify({"code": status_code, "result": result})
