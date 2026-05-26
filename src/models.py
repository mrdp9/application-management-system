from pydantic import BaseModel, field_validator
from typing import Dict, Union
from datetime import datetime, timezone

FlatValue = Union[str, int, float, bool]

class Configuration(BaseModel):
    service_name: str
    environment: str
    data: Dict[str, FlatValue]
    created_at: datetime
    updated_at: datetime

    @field_validator('data', mode='before')
    def check_flat_structure(cls, v):
        """
        Validates that the configuration data is a flat dictionary.
        This runs before Pydantic attempts to coerce values so nested objects
        can be rejected with a clear error message.
        """
        if not isinstance(v, dict):
            raise ValueError("Configuration data must be a dictionary.")

        for key, value in v.items():
            if isinstance(value, (dict, list)):
                raise ValueError(f"Configuration data must be flat. Key '{key}' contains nested data.")
        return v