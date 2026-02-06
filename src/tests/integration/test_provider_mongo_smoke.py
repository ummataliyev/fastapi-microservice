"""
Integration tests for test provider mongo smoke.
"""

import pytest

from src.core.settings import settings


@pytest.mark.integration
@pytest.mark.mongo
def test_mongo_provider_selected():
    """
    Test mongo provider selected.

    :return: None.
    :raises Exception: If the operation fails.
    """
    assert settings.db_provider.lower() == "mongo"
