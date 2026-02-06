"""
Unit tests for test settings.
"""

import pytest

from src.core.settings import Settings


def test_trusted_hosts_wildcard_allowed_in_development(monkeypatch):
    """
    Test trusted hosts wildcard allowed in development.

    :param monkeypatch: TODO - describe monkeypatch.
    :return: None.
    :raises Exception: If the operation fails.
    """
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("TRUSTED_HOSTS", "*")
    cfg = Settings()
    assert cfg.trusted_hosts == ["*"]


def test_trusted_hosts_wildcard_forbidden_in_production(monkeypatch):
    """
    Test trusted hosts wildcard forbidden in production.

    :param monkeypatch: TODO - describe monkeypatch.
    :return: None.
    :raises Exception: If the operation fails.
    """
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("TRUSTED_HOSTS", "*")
    with pytest.raises(ValueError):
        Settings()
