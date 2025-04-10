import random
import string

def generate_short_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric short code.

    Args:
        length (int, optional): The length of the generated short code. Defaults to 6.

    Returns:
        str: A randomly generated alphanumeric string of the specified length.
    """
    """Generate a random alphanumeric short code."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))