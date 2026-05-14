from app.backend.app.core.security import verify_password


def test_verify_password_accepts_seeded_bcrypt_hash():
    password_hash = "$2b$12$udxQAJyAC4wZKM6UjEkor.Gne2d86EwvkPMrRx8BjKFtIVUzgsAsm"

    assert verify_password("password123", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False
