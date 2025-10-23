def complex_payload(*args, **overrides):
    payload = {
        "name": {"en": "Complex X", "ru": "Комплекс X", "uz": "Kompleks X"},
        "address": {
            "en": "Default Address EN",
            "ru": "Адрес по умолчанию",
            "uz": "Standart manzil",
        },
        "parking_space_quantity": 5,
        "status": "active",
    }
    payload.update(overrides)
    return payload
