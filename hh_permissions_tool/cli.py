"""Command line interface for the HH Permissions Tool."""

import os
from pathlib import Path
from typing import Optional, List
import asyncio

import rich_click as click
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.traceback import install
from rich.prompt import Confirm
from google.cloud import asset_v1, resourcemanager_v3
from google.cloud.asset_v1 import Asset
from google.api_core import exceptions
from google.iam.v1 import iam_policy_pb2
from google.oauth2 import service_account
from google.auth import credentials

# Install rich traceback handler
install(show_locals=True)

# Initialize rich console
console = Console()

# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "yellow italic"
click.rich_click.ERRORS_SUGGESTION = "Try running the '--help' command for more information"

def show_welcome_message():
    """Display a welcome message with style."""
    title = "[bold blue]HH Permissions Tool[/bold blue]"
    subtitle = "[cyan]Your Cloud Permissions Audit Assistant[/cyan]"
    version = f"[dim]v{__import__('hh_permissions_tool').__version__}[/dim]"
    
    panel = Panel.fit(
        f"{title}\n{subtitle}\n{version}",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)

def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging settings."""
    logger.remove()  # Remove default handler
    logger.add(
        sink=lambda msg: console.print(msg, highlight=False),
        level=log_level,
        format="<dim>{time:YYYY-MM-DD HH:mm:ss}</dim> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

def load_environment(env_file: Optional[str] = None) -> None:
    """Load environment variables from .env file."""
    if env_file:
        env_path = Path(env_file)
    else:
        env_path = Path(".env")
    
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
    else:
        logger.warning(f"No environment file found at {env_path}")

async def get_project_permissions(project_id: str) -> List[dict]:
    """Get IAM permissions for a Google Cloud project."""
    try:
        # Load credentials from the service account file
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Create IAM client with explicit credentials
        client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        
        # Format the project name
        project_name = f"projects/{project_id}"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Analyzing project permissions...", total=None)
            
            try:
                # Get project IAM policy
                request = iam_policy_pb2.GetIamPolicyRequest(
                    resource=project_name
                )
                
                policy = await asyncio.to_thread(
                    client.get_iam_policy,
                    request=request
                )
                
                # Process and format the results
                results = []
                for binding in policy.bindings:
                    results.append({
                        "role": binding.role,
                        "members": list(binding.members),
                        "resource": project_name
                    })
                
                progress.update(task, completed=True)
                return results
                
            except exceptions.PermissionDenied as e:
                logger.error(f"Permission denied: {str(e)}")
                console.print("[red]Error:[/red] Insufficient permissions. Please ensure your service account has the 'roles/viewer' role.")
                return []
            except exceptions.NotFound as e:
                logger.error(f"Project not found: {str(e)}")
                console.print(f"[red]Error:[/red] Project {project_id} not found.")
                return []
            except Exception as e:
                logger.error(f"Error analyzing permissions: {str(e)}")
                console.print("[red]Error:[/red] Failed to analyze permissions. Check if required APIs are enabled.")
                return []
                
    except Exception as e:
        logger.error(f"Failed to initialize client: {str(e)}")
        console.print("[red]Error:[/red] Failed to initialize Google Cloud client. Check your service account credentials.")
        return []

def display_permissions_table(permissions: List[dict]):
    """Display permissions in a formatted table."""
    table = Table(
        title="[bold blue]Google Cloud IAM Permissions[/bold blue]",
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Role", style="cyan", no_wrap=True)
    table.add_column("Members", style="green")
    table.add_column("Resource", style="yellow", no_wrap=True)
    
    for perm in permissions:
        table.add_row(
            perm["role"],
            "\n".join(perm["members"]),
            perm["resource"]
        )
    
    console.print(table)

@click.group()
@click.option(
    "--env-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to environment file",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Set the logging level",
)
def cli(env_file: Optional[str], log_level: str) -> None:
    """[bold blue]HH Permissions Tool[/bold blue] - Manage and audit permissions effectively.
    
    This tool helps you manage and analyze permissions across your cloud infrastructure.
    """
    show_welcome_message()
    setup_logging(log_level)
    load_environment(env_file)
    logger.info("HH Permissions Tool started")

@cli.command()
@click.option(
    "--project-id",
    help="Google Cloud Project ID to audit",
    envvar="GOOGLE_CLOUD_PROJECT",
)
def audit_gcp(project_id: str):
    """[green]Audit Google Cloud Platform permissions[/green]
    
    This command analyzes IAM permissions in your Google Cloud project and displays them in a formatted table.
    """
    if not project_id:
        console.print("[red]Error:[/red] Project ID is required. Please provide it via --project-id or GOOGLE_CLOUD_PROJECT environment variable.")
        return
    
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        console.print("[red]Error:[/red] Google Cloud credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        return
    
    # Confirm before proceeding
    if not Confirm.ask(f"[yellow]Do you want to audit permissions for project[/yellow] [bold cyan]{project_id}[/bold cyan]?"):
        return
    
    try:
        # Run the async function
        permissions = asyncio.run(get_project_permissions(project_id))
        
        if permissions:
            display_permissions_table(permissions)
        else:
            console.print("[yellow]No permissions found for this project.[/yellow]")
    except Exception as e:
        logger.error(f"Failed to run audit: {str(e)}")
        console.print("[red]Failed to run permissions audit. Please check your credentials and project configuration.[/red]")

@cli.command()
def version():
    """[blue]Display the current version[/blue]"""
    from hh_permissions_tool import __version__
    console.print(f"[bold blue]HH Permissions Tool[/bold blue] [cyan]v{__version__}[/cyan]")

if __name__ == "__main__":
    cli()
