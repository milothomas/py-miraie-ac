"""A group of utility functions"""

def to_float(value: str) -> float:
    """Converts a string to a float type"""
    if value is None:
        return -1.0
    try:
        return float(value)
    except:
        return -1.0
