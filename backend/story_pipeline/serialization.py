from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID


def to_json_value(value):
    """Convert PostgreSQL result values into JSON-compatible API values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: to_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_value(item) for item in value]
    return value
