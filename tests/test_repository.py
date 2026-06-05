import pytest
from datetime import datetime, timezone

from src.models import Configuration
from src.repository import InMemoryConfigRepository


def test_add_environment_and_service():
    repo = InMemoryConfigRepository()

    repo.add_environment("dev")
    repo.add_service("payments", "dev")

    assert repo.list_services() == {"dev": ["payments"]}


def test_add_environment_duplicate_raises_value_error():
    repo = InMemoryConfigRepository()

    repo.add_environment("dev")
    with pytest.raises(ValueError, match="already exists"):
        repo.add_environment("dev")


def test_add_service_duplicate_raises_value_error():
    repo = InMemoryConfigRepository()
    repo.add_environment("dev")
    repo.add_service("payments", "dev")

    with pytest.raises(ValueError, match="already exists"):
        repo.add_service("payments", "dev")


def test_add_service_missing_environment_raises_value_error():
    repo = InMemoryConfigRepository()

    with pytest.raises(ValueError, match="does not exist"):
        repo.add_service("payments", "dev")


def test_save_config_requires_existing_service_and_environment():
    repo = InMemoryConfigRepository()
    repo.add_environment("dev")

    config = Configuration(
        service_name="payments",
        environment="dev",
        data={"key": "value"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="Service 'payments' does not exist"):
        repo.save_config(config)


def test_get_config_returns_saved_configuration():
    repo = InMemoryConfigRepository()
    repo.add_environment("dev")
    repo.add_service("payments", "dev")

    config = Configuration(
        service_name="payments",
        environment="dev",
        data={"key": "value"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    repo.save_config(config)
    assert repo.get_config("payments", "dev") == config
