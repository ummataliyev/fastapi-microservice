"""
Pagination-related configuration.
Defines settings for pagination behavior in the application.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class PaginationSettings(BaseSettings):
    """
    Pagination-related configuration.
    """

    model_config = SettingsConfigDict()

    max_entities_per_page: int = Field(
        default=100,
        ge=1,
        le=1000,
        alias="MAX_ENTITIES_PER_PAGE",
        description="Maximum number of entities per page",
    )
