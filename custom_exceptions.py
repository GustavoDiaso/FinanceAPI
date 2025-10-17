class NonExistentDateError(Exception):
    """This error object will be raised when a Date does not exist"""

    pass


class BadRequestError(Exception):
    pass


class InvalidBrapiAPIKeyError(Exception):
    pass


class MissingBrapiAPIKeyError(Exception):
    pass
