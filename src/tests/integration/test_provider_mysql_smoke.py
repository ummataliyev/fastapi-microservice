"""
Integration tests for test provider mysql smoke.
"""

import pytest

from src.core.settings import settings


@pytest.mark.integration
@pytest.mark.mysql
def test_mysql_provider_selected():
    """
    Test mysql provider selected.

    :return: None.
    :raises Exception: If the operation fails.
    """
    assert settings.db_provider.lower() == "mysql"
