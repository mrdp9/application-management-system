from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Tuple
from .models import Configuration

class ConfigRepository(ABC):
    """Abstract interface for configuration storage."""
    
    @abstractmethod
    def add_environment(self, environment: str) -> None:
        pass
        
    @abstractmethod
    def add_service(self, service_name: str, environment: str) -> None:
        pass
        
    @abstractmethod
    def save_config(self, config: Configuration) -> None:
        pass
        
    @abstractmethod
    def get_config(self, service_name: str, environment: str) -> Optional[Configuration]:
        pass
        
    @abstractmethod
    def list_services(self) -> Dict[str, List[str]]:
        pass

class InMemoryConfigRepository(ConfigRepository):
    """In-memory implementation of the ConfigRepository."""
    
    def __init__(self):
        # Using a Set for fast lookups
        self.environments: Set[str] = set()
        
        # Maps an environment to a set of service names: {"staging": {"payment-service"}}
        self.services: Dict[str, Set[str]] = {}
        
        # Maps a tuple of (service_name, environment) to the Configuration object
        self.configs: Dict[Tuple[str, str], Configuration] = {}

    def add_environment(self, environment: str) -> None:
        if environment in self.environments:
            raise ValueError(f"Environment '{environment}' already exists.")
        self.environments.add(environment)
        self.services[environment] = set()

    def add_service(self, service_name: str, environment: str) -> None:
        if environment not in self.environments:
            raise ValueError(f"Environment '{environment}' does not exist. Please add it first.")
        if service_name in self.services[environment]:
            raise ValueError(f"Service '{service_name}' already exists in '{environment}'.")
        self.services[environment].add(service_name)

    def save_config(self, config: Configuration) -> None:
        # Validate that the env and service actually exist before saving
        if config.environment not in self.environments:
            raise ValueError(f"Environment '{config.environment}' does not exist.")
        if config.service_name not in self.services.get(config.environment, set()):
            raise ValueError(f"Service '{config.service_name}' does not exist in '{config.environment}'.")
        
        key = (config.service_name, config.environment)
        self.configs[key] = config

    def get_config(self, service_name: str, environment: str) -> Optional[Configuration]:
        return self.configs.get((service_name, environment))

    def list_services(self) -> Dict[str, List[str]]:
        # Returns a dict of environments and their respective services
        return {env: list(srvs) for env, srvs in self.services.items()}