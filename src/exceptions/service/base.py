"""
Base service exceptions.
"""


class BaseServiceException(Exception):
    """
    Base class for all service-level exceptions.

    Attributes:
        detail (str): Default message describing the exception.

    :param args: Optional arguments to override the default message.
    :return: None
    """

    message = "Internal server error"

    def __init__(self, *args):
        if not args:
            args = (self.message,)

        super().__init__(*args)
