"""
Unit tests for test mappers base.
"""

from pydantic import BaseModel

from src.mappers.base import BaseDataMapper


class DummySchema(BaseModel):
    """
    DummySchema class.
    :raises Exception: If class initialization or usage fails.
    """

    email: str


class DummyModel:
    """
    DummyModel class.
    :raises Exception: If class initialization or usage fails.
    """

    def __init__(self, email: str):
        """
          init  .

        :param email: TODO - describe email.
        :type email: str
        :return: None.
        :raises Exception: If the operation fails.
        """
        self.email = email


class DummyMapper(BaseDataMapper):
    """
    DummyMapper class.
    :raises Exception: If class initialization or usage fails.
    """

    model = DummyModel
    schema = DummySchema


def test_mapper_to_domain_entity():
    """
    Test mapper to domain entity.

    :return: None.
    :raises Exception: If the operation fails.
    """

    model = DummyModel(email="user@example.com")
    mapped = DummyMapper.map_to_domain_entity(model)
    assert mapped.email == "user@example.com"


def test_mapper_to_persistence_entity():
    """
    Test mapper to persistence entity.

    :return: None.
    :raises Exception: If the operation fails.
    """

    schema = DummySchema(email="user@example.com")
    mapped = DummyMapper.map_to_persistence_entity(schema)
    assert isinstance(mapped, DummyModel)
    assert mapped.email == "user@example.com"


def test_mapper_raises_when_schema_not_configured():
    """
    Test mapper raises when schema not configured.

    :return: None.
    :raises Exception: If the operation fails.
    """

    class BrokenMapper(BaseDataMapper):
        """
        BrokenMapper class.
        :raises Exception: If class initialization or usage fails.
        """
        model = DummyModel
        schema = None

    try:
        BrokenMapper.map_to_domain_entity(DummyModel(email="x@example.com"))
        assert False, "Expected ValueError for missing schema"
    except ValueError as ex:
        assert "schema is not configured" in str(ex)


def test_mapper_raises_when_model_not_configured():
    """
    Test mapper raises when model not configured.

    :return: None.
    :raises Exception: If the operation fails.
    """

    class BrokenMapper(BaseDataMapper):
        """
        BrokenMapper class.
        :raises Exception: If class initialization or usage fails.
        """
        model = None
        schema = DummySchema

    try:
        BrokenMapper.map_to_persistence_entity(DummySchema(email="x@example.com"))
        assert False, "Expected ValueError for missing model"
    except ValueError as ex:
        assert "model is not configured" in str(ex)
