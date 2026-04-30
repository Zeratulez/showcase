import random
import string

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=30))

def random_float() -> float:
    return random.random()