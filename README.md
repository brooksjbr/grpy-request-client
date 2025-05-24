[![Tests](https://github.com/brooksjbr/grpy-request-client/actions/workflows/test.yml/badge.svg)](https://github.com/brooksjbr/grpy-request-client/actions/workflows/test.yml)
[![Lint](https://github.com/brooksjbr/grpy-request-client/actions/workflows/lint.yml/badge.svg)](https://github.com/brooksjbr/grpy-request-client/actions/workflows/lint.yml)

# GRPY Request Client

A Python package for making asynchronous HTTP requests.

## Features

-   **Async-First Design**: Built on aiohttp for efficient asynchronous requests, optimized for high-throughput microservices
-   **Robust Error Handling**:
    -   Comprehensive exception handling with detailed logging
    -   Status code management
    -   Context-aware error reporting
-   **Resource Management**:
    -   Proper session lifecycle management with AsyncExitStack
    -   Automatic cleanup of resources

### From Source

Clone the repository and install the package:

```bash
git clone https://github.com/brooksjbr/grpy-request-client.git
cd grpy-request-client
pip install -e .
```

### Development Environment Setup

This project includes a bootstrap script to set up a virtual environment:

```bash
# Set the path where you want to create the virtual environment
export PYTHON_VENV_PATH=~/venvs
# Run the bootstrap script
python scripts/bootstrap_venv.py
```

After running the script, activate the virtual environment:

```bash
source ~/venvs/grpy-request-client/bin/activate
```

#

### Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/grpy_rest_client
```

### Code Style

This project uses:

-   Black for code formatting
-   Flake8 for linting
-   isort for import sorting

To check code style:

```bash
# Check formatting
black --check src tests

# Check linting
flake8 src tests

# Check import sorting
isort --check-only src tests
```

To automatically format code:

```bash
black src tests
isort src tests
```

### Commit Message Format

This project follows [Conventional Commits](https://www.conventionalcommits.org/) for commit messages. This enables automatic versioning and changelog generation.

Basic format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types include:

-   `feat`: A new feature
-   `fix`: A bug fix
-   `docs`: Documentation changes
-   `style`: Code style changes (formatting, etc.)
-   `refactor`: Code changes that neither fix bugs nor add features
-   `perf`: Performance improvements
-   `test`: Adding or correcting tests
-   `build`: Changes to build system or dependencies
-   `ci`: Changes to CI configuration
-   `chore`: Other changes that don't modify src or test files

For breaking changes, add an exclamation mark before the colon and include a "BREAKING CHANGE:" section in the footer.

## Versioning

This project uses [Semantic Versioning](https://semver.org/) and automatically generates version numbers based on commit messages using python-semantic-release.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
