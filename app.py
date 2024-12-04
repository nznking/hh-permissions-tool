#!/usr/bin/env python3

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Initialize Typer app and console
app = typer.Typer(
    name="gcp-iam",
    help="CLI tool for managing Google Cloud IAM permissions",
    add_completion=False,
)
console = Console()

class GCPPermissionHelper:
    """Helper class to manage and generate Google Cloud IAM permissions."""
    
    # Note: COMMON_SERVICES dictionary remains the same as before
    COMMON_SERVICES = {
        'compute': {
            'viewer': 'roles/compute.viewer',
            'admin': 'roles/compute.admin',
            # ... (previous services remain the same)
        },
        # ... (all other services remain the same)
    }

    def __init__(self):
        self.custom_roles: Dict[str, List[str]] = {}
        self._load_env()

    def _load_env(self):
        """Load environment variables."""
        load_dotenv()
        self.default_project = os.getenv('GCP_PROJECT_ID')
        self.default_region = os.getenv('GCP_REGION', 'us-central1')
        self.default_zone = os.getenv('GCP_ZONE', 'us-central1-a')

    @property
    def project_id(self) -> str:
        """Get the project ID from environment or raise error."""
        if not self.default_project:
            raise typer.BadParameter(
                "GCP_PROJECT_ID must be set in environment or .env file"
            )
        return self.default_project

    def list_available_services(self) -> List[str]:
        """List all available services."""
        return sorted(list(self.COMMON_SERVICES.keys()))

    def list_service_roles(self, service: str) -> List[str]:
        """List all available roles for a specific service."""
        if service not in self.COMMON_SERVICES:
            raise ValueError(f"Service {service} not found in common services")
        return sorted(list(self.COMMON_SERVICES[service].keys()))

    def generate_service_permissions(self, service: str, level: str = 'viewer') -> Set[str]:
        """Generate permissions for a service and level."""
        if service not in self.COMMON_SERVICES:
            raise ValueError(f"Service {service} not found in common services")
            
        if level not in self.COMMON_SERVICES[service]:
            raise ValueError(f"Level {level} not found for service {service}")
            
        return {self.COMMON_SERVICES[service][level]}

    def generate_terraform_config(self, project_id: str, role_name: str) -> str:
        """Generate Terraform configuration for a custom role."""
        if role_name not in self.custom_roles:
            raise ValueError(f"Custom role {role_name} not found")

        return f"""
resource "google_project_iam_custom_role" "{role_name}" {{
  project     = "{project_id}"
  role_id     = "{role_name}"
  title       = "{role_name.replace('_', ' ').title()}"
  description = "Custom role for {role_name}"
  permissions = {json.dumps(self.custom_roles[role_name], indent=4)}
}}
"""

# CLI Commands

@app.command()
def list_services():
    """List all available GCP services."""
    helper = GCPPermissionHelper()
    services = helper.list_available_services()
    
    table = Table(title="Available GCP Services")
    table.add_column("Service Name", style="cyan")
    table.add_column("Available Roles", style="green")
    
    for service in services:
        roles = ", ".join(helper.list_service_roles(service))
        table.add_row(service, roles)
    
    console.print(table)

@app.command()
def list_roles(
    service: str = typer.Argument(..., help="GCP service name"),
):
    """List available roles for a specific service."""
    helper = GCPPermissionHelper()
    try:
        roles = helper.list_service_roles(service)
        
        table = Table(title=f"Available Roles for {service}")
        table.add_column("Role Name", style="cyan")
        table.add_column("Full Role ID", style="green")
        
        for role in roles:
            full_role = helper.COMMON_SERVICES[service][role]
            table.add_row(role, full_role)
        
        console.print(table)
    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def generate(
    service: str = typer.Argument(..., help="GCP service name"),
    level: str = typer.Option("viewer", help="Access level"),
    project_id: str = typer.Option(None, help="GCP project ID (overrides env)"),
    output: Path = typer.Option(None, help="Output file for Terraform config"),
):
    """Generate Terraform configuration for a service role."""
    helper = GCPPermissionHelper()
    
    try:
        project = project_id or helper.project_id
        permissions = helper.generate_service_permissions(service, level)
        role_name = f"custom_{service}_{level}"
        helper.custom_roles[role_name] = list(permissions)
        
        tf_config = helper.generate_terraform_config(project, role_name)
        
        if output:
            output.write_text(tf_config)
            rprint(f"[green]Configuration written to {output}[/green]")
        else:
            print(tf_config)
            
    except (ValueError, typer.BadParameter) as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def init():
    """Initialize configuration with a new .env file."""
    if Path(".env").exists():
        overwrite = typer.confirm("A .env file already exists. Overwrite it?")
        if not overwrite:
            raise typer.Exit()
    
    project_id = typer.prompt("GCP Project ID")
    region = typer.prompt("GCP Region", default="us-central1")
    zone = typer.prompt("GCP Zone", default="us-central1-a")
    
    env_content = f"""# GCP Configuration
GCP_PROJECT_ID={project_id}
GCP_REGION={region}
GCP_ZONE={zone}
"""
    
    Path(".env").write_text(env_content)
    rprint("[green]Configuration file .env created successfully![/green]")

if __name__ == "__main__":
    app()