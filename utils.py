
def toFloat(value: str) -> float:
    if value is None:
        return -1.0
    try:
        return float(value)
    except:
        return -1.0
