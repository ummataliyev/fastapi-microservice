"""
Residential Complex Repository
"""

from src.models.complex import Complex

from src.mappers.base import BaseDataMapper

from src.schemas.complex import ComplexReadSchema
from src.schemas.complex import ComplexReadWithRelationsSchema


class ComplexMapper(BaseDataMapper):
    """
    Mapper between Complex model and its schemas.

    Attributes:
        model (Complex): SQLAlchemy model for complexes.
        schema (ComplexReadSchema): Schema without relations.
        schema_with_rels (ComplexReadWithRelationsSchema): Schema with relations.

    :param model: The Complex database model.
    :param schema: Schema for Complex without related entities.
    :param schema_with_rels: Schema for Complex with related entities.
    :return: A configured mapper class for Complex objects.
    """

    model = Complex
    schema = ComplexReadSchema
    schema_with_rels = ComplexReadWithRelationsSchema
