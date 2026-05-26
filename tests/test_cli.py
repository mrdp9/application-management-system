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

    result = runner.invoke(app_module.app, ["add-environment", "dev"])
    assert result.exit_code == 0
    assert "Success" in result.stdout
    assert "Environment 'dev' added" in result.stdout


def test_add_service_command(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("dev")

    result = runner.invoke(app_module.app, ["add-service", "payments", "dev"])
    assert result.exit_code == 0
    assert "Service 'payments' added to 'dev'" in result.stdout


def test_set_config_with_key_value_pair(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("dev")
    repo.add_service("payments", "dev")

    result = runner.invoke(app_module.app, ["set-config", "payments", "dev", "timeout_seconds", "30"])
    assert result.exit_code == 0
    assert "Configuration set for 'payments' in 'dev'" in result.stdout
    assert repo.get_config("payments", "dev").data == {"timeout_seconds": 30}


def test_set_and_get_config_command(monkeypatch):
    repo = make_fresh_controller(monkeypatch)
    repo.add_environment("dev")
    repo.add_service("payments", "dev")

    payload = json.dumps({"host": "localhost", "port": 8080})
    result = runner.invoke(app_module.app, ["set-config", "payments", "dev", payload])
    assert result.exit_code == 0
    assert "Configuration set for 'payments' in 'dev'" in result.stdout

    result = runner.invoke(app_module.app, ["get-config", "payments", "dev"])
    assert result.exit_code == 0
    assert '"host": "localhost"' in result.stdout
    assert '"port": 8080' in result.stdout


def test_set_config_invalid_json_produces_error(monkeypatch):
    make_fresh_controller(monkeypatch)

    result = runner.invoke(app_module.app, ["set-config", "payments", "dev", "not-json"])
    assert result.exit_code == 0
    assert "Invalid JSON format" in result.stdout


def test_list_services_empty_shows_message(monkeypatch):
    make_fresh_controller(monkeypatch)

    result = runner.invoke(app_module.app, ["list-services"])
    assert result.exit_code == 0
    assert "No environments or services found" in result.stdout
