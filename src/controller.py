import copy
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import ValidationError
from .models import Configuration, FlatValue
from .repository import ConfigRepository

class ConfigController:
    """Handles business logic and orchestrates data between CLI and Repository."""
    
    def __init__(self, repository: ConfigRepository):
        self.repo = repository

    def add_environment(self, environment: str) -> None:
        self.repo.add_environment(environment)

    def add_service(self, service_name: str, environment: str) -> None:
        self.repo.add_service(service_name, environment)

    def set_config(self, service_name: str, environment: str, data: Dict[str, FlatValue]) -> None:
        """Creates a completely new configuration or overwrites an existing one."""
        now = datetime.now(timezone.utc)
        
        # Creating this object automatically triggers Pydantic's validation!
        try:
            config = Configuration(
                service_name=service_name,
                environment=environment,
                data=data,
                created_at=now,
                updated_at=now
            )
        except ValidationError as exc:
            raise ValueError(str(exc)) from exc

        self.repo.save_config(config)

    def update_config(self, service_name: str, environment: str, partial_data: Dict[str, FlatValue]) -> None:
        """
        Partially updates a configuration ensuring atomicity (all-or-nothing).
        If validation fails on the new data, the old data remains untouched.
        """
        existing_config = self.repo.get_config(service_name, environment)
        if not existing_config:
            raise ValueError(f"No configuration found for '{service_name}' in '{environment}'. Use 'set-config' first.")

        # 1. Create a deep copy of the existing data to prevent partial mutation
        new_data = copy.deepcopy(existing_config.data)
        
        # 2. Apply the updates to our copy
        new_data.update(partial_data)

        # 3. Create a NEW Configuration object. 
        # If Pydantic validation fails here, it raises an error BEFORE saving,
        # ensuring our atomic update requirement is perfectly met.
        try:
            updated_config = Configuration(
                service_name=service_name,
                environment=environment,
                data=new_data,
                created_at=existing_config.created_at,  # Keep original creation time
                updated_at=datetime.now(timezone.utc)   # Update modification time
            )
        except ValidationError as exc:
            raise ValueError(str(exc)) from exc

        # 4. Save back to the repository
        self.repo.save_config(updated_config)

    def get_config(self, service_name: str, environment: str) -> Optional[Configuration]:
        return self.repo.get_config(service_name, environment)

    def list_services(self) -> Dict[str, List[str]]:
        return self.repo.list_services()