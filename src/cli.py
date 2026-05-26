import json
import shlex
import sys
import typer
from rich.console import Console
from .repository import InMemoryConfigRepository
from .controller import ConfigController
from typing import Optional

# Initialize the Typer app and Rich console
app = typer.Typer(help="Application Configuration Service CLI")
console = Console()


def _coerce_config_value(value: str):
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)

    try:
        float_value = float(value)
        if "." in value or "e" in value.lower():
            return float_value
    except ValueError:
        pass

    return value


def _parse_config_input(data: str, value: Optional[str] = None):
    if value is not None:
        return {data: _coerce_config_value(value)}

    return json.loads(data)

# Initialize our in-memory storage and controller
# State will persist as long as this script remains running
repo = InMemoryConfigRepository()
controller = ConfigController(repo)

@app.command("add-environment")
def add_environment(environment: str):
    """Add a new environment (e.g., dev, staging, production)."""
    try:
        controller.add_environment(environment)
        console.print(f"[bold green]Success:[/bold green] Environment '{environment}' added.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command("add-service")
def add_service(service_name: str, environment: str):
    """Add a new service to an existing environment."""
    try:
        controller.add_service(service_name, environment)
        console.print(f"[bold green]Success:[/bold green] Service '{service_name}' added to '{environment}'.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command("set-config")
def set_config(
    service_name: str,
    environment: str,
    data: str,
    value: Optional[str] = typer.Argument(None),
):
    """Set configuration for a service.

    Provide either a JSON object or a single key/value pair.
    Examples:
      config set-config payment-service production '{"timeout_seconds": 30}'
      config set-config payment-service production timeout_seconds 30
    """
    try:
        json_data = _parse_config_input(data, value)
        controller.set_config(service_name, environment, json_data)
        console.print(f"[bold green]Success:[/bold green] Configuration set for '{service_name}' in '{environment}'.")
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/bold red] Invalid JSON format. Please provide a valid JSON string.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command("update-config")
def update_config(
    service_name: str,
    environment: str,
    data: str,
    value: Optional[str] = typer.Argument(None),
):
    """Update existing configuration atomically.

    Provide either a JSON object or a single key/value pair.
    Examples:
      config update-config payment-service production '{"timeout_seconds": 30}'
      config update-config payment-service production timeout_seconds 30
    """
    try:
        json_data = _parse_config_input(data, value)
        controller.update_config(service_name, environment, json_data)
        console.print(f"[bold green]Success:[/bold green] Configuration updated atomically for '{service_name}' in '{environment}'.")
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/bold red] Invalid JSON format. Please provide a valid JSON string.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command("get-config")
def get_config(service_name: str, environment: str):
    """Retrieve the configuration for a service in an environment."""
    config = controller.get_config(service_name, environment)
    if config:
        # Use Rich to print pretty JSON
        console.print_json(config.model_dump_json())
    else:
        console.print(f"[bold yellow]Not Found:[/bold yellow] No configuration for '{service_name}' in '{environment}'.")

@app.command("list-services")
def list_services():
    """List all onboarded environments and their associated services."""
    services = controller.list_services()
    if not services:
        console.print("[yellow]No environments or services found.[/yellow]")
        return
    
    for env, srvs in services.items():
        console.print(f"[bold blue]Environment:[/bold blue] {env}")
        for srv in srvs:
            console.print(f"  - {srv}")

def interactive_shell():
    """Starts an interactive loop to keep the in-memory state alive."""
    console.print("[bold blue]Welcome to the Config Service Interactive CLI.[/bold blue]")
    console.print("Type your commands (e.g., [green]add-environment dev[/green]) or '[red]exit[/red]' to quit.")
    
    while True:
        try:
            # The prompt
            user_input = input("\nconfig> ")
            
            if user_input.strip().lower() in ['exit', 'quit']:
                console.print("Goodbye!")
                break
            if not user_input.strip():
                continue
            
            # Use shlex to correctly parse strings with quotes (like JSON)
            args = shlex.split(user_input)
            
            # Execute the Typer app with the parsed arguments
            app(args, standalone_mode=False)
            
        except typer.Exit:
            pass # Prevent Typer from killing the loop on successful command run
        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    # If the user passes arguments directly, run as a standard CLI
    if len(sys.argv) > 1:
        app()
    # Otherwise, boot up the interactive shell to keep memory alive
    else:
        interactive_shell()