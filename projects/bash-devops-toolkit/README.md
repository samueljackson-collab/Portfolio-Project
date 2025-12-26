# Bash DevOps Toolkit

A collection of Bash automation scripts for infrastructure, backups, deployments, and operational utilities.

## Features

- ShellCheck-friendly Bash (`set -euo pipefail`)
- Structured logging with dry-run support
- Environment variable configuration
- BATS tests and example usage

## Installation

```bash
chmod +x scripts/*.sh
```

## Usage

Each script supports `--help` for details.

```bash
./scripts/docker_cleanup.sh --help
```

## Documentation

Detailed documentation is available per script in the `docs/` directory.

## Testing

```bash
bats tests
```

## Linting

```bash
shellcheck scripts/*.sh lib/common.sh
```
