import json

from typer.testing import CliRunner

from src import cli as app_module
from src.controller import ConfigController
from src.repository import InMemoryConfigRepository


runner = CliRunner()


def make_fresh_controller(monkeypatch):
    repo = InMemoryConfigRepository()
    controller = ConfigController(repo)
    monkeypatch.setattr(app_module, "controller", controller)
    return repo


def test_add_environment_command(monkeypatch):
    make_fresh_controller(monkeypatch)

    result = runner.invoke(app_module.app, ["add-environment", "staging"])
    assert result.exit_code == 0
    assert "Success" in result.stdout
    assert "Environment 'staging' added" in result.stdout


def test_add_service_command(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("staging")

    result = runner.invoke(app_module.app, ["add-service", "payment-service", "staging"])
    assert result.exit_code == 0
    assert "Service 'payment-service' added to 'staging'" in result.stdout


def test_set_config_command_with_key_value_pair(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("production")
    repo.add_service("payment-service", "production")

    result = runner.invoke(app_module.app, ["set-config", "payment-service", "production", "timeout_seconds", "30"])
    assert result.exit_code == 0
    assert "Configuration set for 'payment-service' in 'production'" in result.stdout
    assert repo.get_config("payment-service", "production").data == {"timeout_seconds": 30}


def test_set_config_command_with_json_payload(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("production")
    repo.add_service("payment-service", "production")

    payload = json.dumps({"timeout_seconds": 30, "retry_attempts": 3, "enable_logging": True})
    result = runner.invoke(app_module.app, ["set-config", "payment-service", "production", payload])
    assert result.exit_code == 0
    assert "Configuration set for 'payment-service' in 'production'" in result.stdout


def test_update_config_command_with_json_payload(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("production")
    repo.add_service("payment-service", "production")
    repo.add_environment("staging")
    repo.add_service("payment-service", "staging")
    repo.get_config = repo.get_config

    result_set = runner.invoke(app_module.app, ["set-config", "payment-service", "production", json.dumps({"timeout_seconds": 30})])
    assert result_set.exit_code == 0

    payload = json.dumps({"timeout_seconds": 60, "retry_attempts": 3, "enable_logging": True})
    result = runner.invoke(app_module.app, ["update-config", "payment-service", "production", payload])
    assert result.exit_code == 0
    assert "Configuration updated atomically for 'payment-service' in 'production'" in result.stdout


def test_get_config_command_returns_configuration(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("production")
    repo.add_service("payment-service", "production")

    payload = json.dumps({"timeout_seconds": 30})
    result = runner.invoke(app_module.app, ["set-config", "payment-service", "production", payload])
    assert result.exit_code == 0

    result = runner.invoke(app_module.app, ["get-config", "payment-service", "production"])
    assert result.exit_code == 0
    assert '"timeout_seconds": 30' in result.stdout


def test_list_services_command_shows_environment_and_service(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("production")
    repo.add_service("payment-service", "production")

    result = runner.invoke(app_module.app, ["list-services"])
    assert result.exit_code == 0
    assert "Environment: production" in result.stdout or "Environment:[" in result.stdout
    assert "payment-service" in result.stdout


def test_set_config_invalid_json_returns_error(monkeypatch):
    make_fresh_controller(monkeypatch)

    result = runner.invoke(app_module.app, ["set-config", "payment-service", "production", "not-json"])
    assert result.exit_code == 0
    assert "Invalid JSON format" in result.stdout
