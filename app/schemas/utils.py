
def check_not_empty_str(error: str):
    def wrapper(value: str):
        value = value.strip()
        if not value:
            raise ValueError(error)
        return value
    return wrapper