"""
Unit tests for Complex Service layer.
"""

import pytest

from src.enums.status import Status

from src.services.users import ComplexService

from src.schemas.users import ComplexReadSchema
from src.schemas.users import ComplexCreateSchema
from src.schemas.users import ComplexUpdateSchema

from src.exceptions.service.users import ComplexNotFound

from src.tests.unit.base.base_crud_test import ServiceTestBase


@pytest.mark.asyncio
class TestComplexService(ServiceTestBase):
    """
    Concrete tests for ComplexService using the reusable template.
    """

    service_cls = ComplexService
    repo_attr = "complex"
    read_schema_cls = ComplexReadSchema
    create_schema_cls = ComplexCreateSchema
    update_schema_cls = ComplexUpdateSchema
    not_found_exc_cls = ComplexNotFound

    default_create_payload = {
        "name": {"en": "Test"},
        "address": {"en": "Addr"},
        "parking_space_quantity": 1,
        "status": Status.UNDER_CONSTRUCTION,
    }

    default_update_payload = {
        "name": {"en": "Updated"},
        "address": {"en": "Addr"},
        "parking_space_quantity": 1,
        "status": Status.ACTIVE,
    }

    default_read_payload = {
        "name": {"en": "Test"},
        "address": {"en": "Addr"},
        "parking_space_quantity": 1,
        "status": Status.ACTIVE,
    }
