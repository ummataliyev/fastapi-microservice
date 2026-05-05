from src.security.implementations.bcrypt import BcryptPasswordHasher


def test_hash_then_verify_returns_true():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("hunter2-secure")
    assert hashed != "hunter2-secure"
    assert hasher.verify("hunter2-secure", hashed) is True


def test_verify_with_wrong_password_returns_false():
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("hunter2-secure")
    assert hasher.verify("wrong-password", hashed) is False
