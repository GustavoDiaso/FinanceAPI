class NonExistentDateError(ValueError):
    """This error object will be raised when a Date does not exist"""

    pass


class StandardAPIErrorMessage:
    def __init__(self, http_error_code: int, error_reason: str, error_explanation: str):
        self.message = {
            "success": False,
            "error": {
                "code": http_error_code,
                "error_reason": error_reason,
                "explanation": error_explanation,
            },
        }

    def to_dict(self) -> dict:
        return self.message


class StandardAPISuccessfulResponse:
    def __init__(self, data: dict):
        self.response = {"success": True, "data": data}

    def to_dict(self) -> dict:
        return self.response
