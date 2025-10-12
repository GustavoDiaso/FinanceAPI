class StandardAPIErrorMessage:
    def __init__(
        self,
        http_error_code: int,
        error_message: str,
    ):
        self.message = {
            "success": False,
            "error": {
                "code": http_error_code,
                "message": error_message,
            },
        }

    def to_dict(self) -> dict:
        return self.message


class StandardAPISuccessfulResponse:
    def __init__(self, data: dict):
        self.response = {"success": True, "data": data}

    def to_dict(self) -> dict:
        return self.response
