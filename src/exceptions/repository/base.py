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

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)


class ObjectNotFoundRepoException(BaseRepoException):
    """
    Raised when the requested database object is not found.
    """
    message = "Object not found in repository"


class CannotAddObjectRepoException(BaseRepoException):
    """
    Raised when the repository fails to add a new object
    due to integrity or constraint violations.
    """
    message = "Cannot add object to repository"


class CannotUpdateObjectRepoException(BaseRepoException):
    """
    Raised when the repository fails to update an existing object.
    """
    message = "Cannot update object in repository"


class CannotDeleteObjectRepoException(BaseRepoException):
    """
    Raised when the repository fails to soft-delete or remove an object.
    """
    message = "Cannot delete object from repository"


class DatabaseConnectionRepoException(BaseRepoException):
    """
    Raised when a database connection or transaction fails.
    """
    message = "Database connection error"
