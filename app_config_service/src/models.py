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

    @field_validator('data')
    def check_flat_structure(cls, v: Dict[str, FlatValue]) -> Dict[str, FlatValue]:
        """
        Validates that the configuration data is a flat dictionary.
        Pydantic's FlatValue type hint catches most nested structures, 
        but this explicitly raises a clear error if complex types slip through.
        """
        for key, value in v.items():
            if isinstance(value, (dict, list)):
                raise ValueError(f"Configuration data must be flat. Key '{key}' contains nested data.")
        return v