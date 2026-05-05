class BaseRepoException(Exception):
    """Root for all repository-layer exceptions."""

    def __init__(self, message: str = "Repository error") -> None:
        super().__init__(message)
        self.message = message


class EntityNotFoundError(BaseRepoException):
    def __init__(self, entity_name: str, entity_id: object) -> None:
        super().__init__(f"{entity_name} with id={entity_id} not found")
        self.entity_name = entity_name
        self.entity_id = entity_id


class EntityAlreadyExistsError(BaseRepoException):
    def __init__(self, entity_name: str, conflict: str) -> None:
        super().__init__(f"{entity_name} already exists: {conflict}")
        self.entity_name = entity_name
        self.conflict = conflict
