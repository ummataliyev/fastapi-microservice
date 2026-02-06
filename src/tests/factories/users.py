"""
Test support for users.
"""


def users_payload(*args, **overrides):
    """
    Users payload.

    :param args: TODO - describe args.
    :param overrides: TODO - describe overrides.
    :return: TODO - describe return value.
    :raises Exception: If the operation fails.
    """
    payload = {
        "email": "djohnummataliyev@gmail.com",
        "password": "password"
    }
    payload.update(overrides)
    return payload
