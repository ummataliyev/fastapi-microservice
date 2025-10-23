# src/tests/factories/building.py
def building_payload(*args, **overrides):
    payload = {
        "name": {"en": "Building Y", "ru": "Здание Y", "uz": "Bino Y"},
        "complex_id": None,
        "status": "under_construction",
    }
    payload.update(overrides)
    return payload
