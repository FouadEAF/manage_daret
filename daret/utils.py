import secrets
import string


def generate_code_group(length=8):
    """Generates a random alphanumeric code of a given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))
