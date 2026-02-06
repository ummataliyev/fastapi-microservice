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
    error_code = "SERVICE_ERROR"

    def __init__(
            self, message: str | None = None,
            details: dict | None = None
    ):
        """
          init  .

        :param message: TODO - describe message.
        :type message: str | None
        :param details: TODO - describe details.
        :type details: dict | None
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """
          str  .

        :return: TODO - describe return value.
        :rtype: str
        :raises Exception: If the operation fails.
        """
        return self.message
