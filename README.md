# HH Permissions Tool 🔐

A powerful and user-friendly CLI tool for auditing and managing permissions across cloud platforms, with initial support for Google Cloud Platform (GCP).

## Features ✨

- 🌟 Beautiful, colorful command-line interface
- 🔍 Comprehensive GCP IAM permissions auditing
- 📊 Rich, formatted output with tables and progress indicators
- 🔐 Secure credential management through environment variables
- 📝 Detailed logging with configurable levels
- 🚀 Cross-platform support (Windows, macOS, Linux)

## Prerequisites 📋

- Python 3.9 or later
- Poetry (will be installed by setup scripts if not present)
- Google Cloud credentials (for GCP auditing features)

## Installation 🛠️

### Automated Setup

#### On Unix/Linux/macOS:
```bash
# Clone the repository
git clone <repository-url>
cd hh-permissions-tool

# Run the setup script
./setup.sh
```

#### On Windows:
```powershell
# Clone the repository
git clone <repository-url>
cd hh-permissions-tool

# Run the setup script
.\setup.ps1
```

### Manual Setup

If you prefer to set up manually:

1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Configure Poetry:
   ```bash
   poetry config virtualenvs.in-project true
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration ⚙️

### Environment Variables

Create a `.env` file in the project root (or copy from `.env.example`):

```ini
# Application Settings
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Google Cloud Settings
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
```

### Google Cloud Setup

1. Create a Google Cloud project or use an existing one
2. Create a service account with necessary permissions:
   - `roles/iam.securityReviewer`
   - `roles/resourcemanager.projectIamAdmin` (read-only access is sufficient)
3. Download the service account key (JSON)
4. Set the path to your credentials in the `.env` file

## Usage 📚

### Basic Commands

1. Activate the virtual environment:
   ```bash
   poetry shell
   ```

2. View available commands:
   ```bash
   python -m hh_permissions_tool.cli --help
   ```

3. Check tool version:
   ```bash
   python -m hh_permissions_tool.cli version
   ```

### Google Cloud Permissions Audit

Audit IAM permissions in your GCP project:

```bash
# Using project ID from environment
python -m hh_permissions_tool.cli audit-gcp

# Or specify project ID directly
python -m hh_permissions_tool.cli audit-gcp --project-id your-project-id
```

### Logging Options

Control log output with the `--log-level` option:

```bash
python -m hh_permissions_tool.cli --log-level DEBUG audit-gcp
```

Available log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical issues

### Environment File

Use a custom environment file:

```bash
python -m hh_permissions_tool.cli --env-file /path/to/custom.env audit-gcp
```

## Output Examples 📊

### GCP Permissions Audit

The `audit-gcp` command produces a formatted table with:
- Role names and descriptions
- Members (users, groups, service accounts)
- Associated resources
- Inheritance information

Example output:
```
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Role                  ┃ Members           ┃ Resource            ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ roles/owner          │ user:admin@...    │ projects/my-project │
│ roles/viewer         │ group:viewers@... │ projects/my-project │
└──────────────────────┴──────────────────┴────────────────────┘
```

## Development 🔧

### Project Structure

```
hh-permissions-tool/
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore patterns
├── README.md            # Project documentation
├── pyproject.toml       # Poetry project configuration
├── setup.ps1            # Windows setup script
├── setup.sh             # Unix setup script
└── hh_permissions_tool/ # Main package directory
    ├── __init__.py     # Package initialization
    └── cli.py          # Command-line interface
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Update tests and documentation
5. Submit a pull request

## Troubleshooting 🔍

### Common Issues

1. **Poetry not found**
   ```bash
   # Add Poetry to your PATH
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **Google Cloud authentication errors**
   - Verify your credentials file path
   - Check service account permissions
   - Ensure project ID is correct

3. **Permission denied running setup.sh**
   ```bash
   chmod +x setup.sh
   ```

### Debug Mode

Run with debug logging for more information:
```bash
python -m hh_permissions_tool.cli --log-level DEBUG audit-gcp
```

## License 📄

[Add your license information here]

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## Support 💬

If you encounter any problems or have questions:
1. Check the troubleshooting section
2. Open an issue on GitHub
3. Contact the maintainers
