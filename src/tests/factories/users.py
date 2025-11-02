def users_payload(*args, **overrides):
    payload = {"name": "djohnummataliyev@gmail.com", "password": "password"}
    payload.update(overrides)
    return payload
