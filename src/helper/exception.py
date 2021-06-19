class CustomException(Exception):
    """Custom exceptions main class."""

    def __init__(self, message):
        super().__init__(message)
        self.__message = message


class MissingMandatoryParameters(CustomException):
    def __init__(self, missing_parameters: list):
        super().__init__(f"Missing mandatory input params: {missing_parameters}")


class FailedBuild(CustomException):
    def __init__(self):
        super().__init__("Build failed")
