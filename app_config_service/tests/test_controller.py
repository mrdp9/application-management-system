import pytest
from datetime import datetime, timezone

from src.controller import ConfigController
from src.models import Configuration
from src.repository import InMemoryConfigRepository


def make_repo_with_service():
    repo = InMemoryConfigRepository()
    repo.add_environment("dev")
    repo.add_service("payments", "dev")
    return repo


def test_set_config_creates_configuration():
    repo = make_repo_with_service()
    controller = ConfigController(repo)

    controller.set_config("payments", "dev", {"host": "localhost", "port": 8080})

    config = repo.get_config("payments", "dev")
    assert config is not None
    assert config.data == {"host": "localhost", "port": 8080}
    assert config.created_at == config.updated_at


def test_set_config_rejects_nested_data():
    repo = make_repo_with_service()
    controller = ConfigController(repo)

    with pytest.raises(ValueError, match="must be flat"):
        controller.set_config("payments", "dev", {"nested": {"inner": "value"}})


def test_update_config_merges_changes_atomically():
    repo = make_repo_with_service()
    controller = ConfigController(repo)
    controller.set_config("payments", "dev", {"host": "localhost", "port": 8080})

    controller.update_config("payments", "dev", {"port": 9090, "debug": True})

    config = repo.get_config("payments", "dev")
    assert config.data == {"host": "localhost", "port": 9090, "debug": True}


def test_update_config_on_missing_configuration_raises_value_error():
    repo = make_repo_with_service()
    controller = ConfigController(repo)

    with pytest.raises(ValueError, match="No configuration found"):
        controller.update_config("payments", "dev", {"debug": True})


def test_update_config_invalid_partial_data_is_atomic():
    repo = make_repo_with_service()
    controller = ConfigController(repo)
    controller.set_config("payments", "dev", {"host": "localhost", "port": 8080})

    original_data = repo.get_config("payments", "dev").data.copy()
    with pytest.raises(ValueError, match="must be flat"):
        controller.update_config("payments", "dev", {"debug": {"enabled": True}})

    assert repo.get_config("payments", "dev").data == original_data
