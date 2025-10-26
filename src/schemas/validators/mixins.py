"""
Validator mixin for localized fields.
"""

from typing import Dict

from pydantic import BaseModel

from fastapi import HTTPException


LOCALE_KEYS = ("uz", "ru", "en")
MAX_LENGTH = 255


class LocalizedFieldMixin(BaseModel):
    """
    Mixin to validate multilingual/localized dictionary fields.

    Ensures:
        - The value is a dictionary with keys corresponding to `LOCALE_KEYS`.
        - At least one language field must be non-empty.
        - Each filled value must not exceed `MAX_LENGTH`.

    :raises HTTPException 400: If validation fails.
    """

    @classmethod
    def validate_localized(cls, field_name: str, value: Dict[str, str]):
        """
        Validate a multilingual/localized field.

        :param field_name: The name of the field being validated (used in error messages).
        :type field_name: str
        :param value: A dictionary of translations keyed by locale code.
        :type value: Dict[str, str]

        :return: The validated dictionary of localized values.
        :rtype: Dict[str, str] | None

        :raises HTTPException 400:
            - If value is not a dict.
            - If all locales are empty.
            - If any translation exceeds `MAX_LENGTH`.
        """

        if value is None:
            return None

        if not isinstance(value, dict):
            raise HTTPException(status_code=400, detail=f"{field_name} must be a dict")

        filled = False
        for key in LOCALE_KEYS:
            if key in value and value[key]:
                filled = True
                if len(value[key]) > MAX_LENGTH:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{field_name}.{key} must be at most {MAX_LENGTH} chars",
                    )

        if not filled:
            raise HTTPException(
                status_code=400,
                detail=f"At least one language in {field_name} must be filled",
            )

        return value
