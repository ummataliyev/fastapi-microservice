"""
Base repository exceptions.
"""


class BaseRepoException(Exception):
    """
    Base class for all repository-level exceptions.

    This layer isolates raw database errors (IntegrityError, NoResultFound, etc.)
    from upper layers (Service, API).
    """

    message = "Repository operation failed"
    error_code = "REPOSITORY_ERROR"

    def __init__(self, message: str | None = None, details: dict | None = None):
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


class ObjectNotFoundRepoException(BaseRepoException):
    """
    Raised when the requested database object is not found.
    """

    message = "Object not found in repository"
    error_code = "REPOSITORY_OBJECT_NOT_FOUND"


class CannotAddObjectRepoException(BaseRepoException):
    """
    Raised when the repository fails to add a new object
    due to integrity or constraint violations.
    """

    message = "Cannot add object to repository"
    error_code = "REPOSITORY_CANNOT_ADD"


class CannotUpdateObjectRepoException(BaseRepoException):
    """
    Raised when the repository fails to update an existing object.
    """

    message = "Cannot update object in repository"
    error_code = "REPOSITORY_CANNOT_UPDATE"


class CannotDeleteObjectRepoException(BaseRepoException):
    """
    Raised when the repository fails to soft-delete or remove an object.
    """

    message = "Cannot delete object from repository"
    error_code = "REPOSITORY_CANNOT_DELETE"


class DatabaseConnectionRepoException(BaseRepoException):
    """
    Raised when a database connection or transaction fails.
    """

    message = "Database connection error"
    error_code = "REPOSITORY_CONNECTION_ERROR"


class InvalidRepositoryInputRepoException(BaseRepoException):
    """
    Raised when repository receives invalid query/input parameters.
    """

    message = "Invalid repository input"
    error_code = "REPOSITORY_INVALID_INPUT"
