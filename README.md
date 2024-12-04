# HH Permissions Tool

A tool for managing and analyzing permissions effectively.

## Setup

1. Install Poetry (if you haven't already):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository and navigate to it:
   ```bash
   git clone <repository-url>
   cd hh-permissions-tool
   ```

3. Install dependencies and create virtual environment:
   ```bash
   poetry install
   ```

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your desired settings
   ```

## Usage

The tool can be run using Poetry:

```bash
# Show help
poetry run python -m hh_permissions_tool.cli --help

# Run with custom environment file
poetry run python -m hh_permissions_tool.cli --env-file /path/to/.env

# Run with different log level
poetry run python -m hh_permissions_tool.cli --log-level DEBUG
```

## Development

1. Activate the virtual environment:
   ```bash
   poetry shell
   ```

2. Run the tool directly:
   ```bash
   python -m hh_permissions_tool.cli
   ```

## Environment Variables

- `LOG_LEVEL`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Add other environment variables as needed

## Project Structure

```
hh-permissions-tool/
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore file
├── README.md            # Project documentation
├── pyproject.toml       # Poetry project configuration
├── hh_permissions_tool/ # Main package directory
│   ├── __init__.py     # Package initialization
│   └── cli.py          # Command-line interface
```
