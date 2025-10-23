def section_payload(*args, **overrides):
    payload = {
        "building_id": None,
        "name": {"en": "Block A", "ru": "Блок А", "uz": "A Blok"},
        "number": 1,
        "status": "active",
    }
    payload.update(overrides)
    return payload
