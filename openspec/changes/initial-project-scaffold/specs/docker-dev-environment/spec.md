## Purpose

Gives a developer a one-command local environment (Odoo 19 + Postgres via Docker Compose) to run Inventory Management and verify it installs correctly, without requiring a manual Odoo/Postgres install on the host machine.

## ADDED Requirements

### Requirement: One-command environment startup
The project SHALL provide a Docker Compose configuration that starts an Odoo 19 instance and a Postgres database with a single command.

#### Scenario: Starting the environment
- **WHEN** a developer runs `docker compose up` in the repo root
- **THEN** an Odoo 19 container and a Postgres container start and Odoo becomes reachable in a browser on the configured local port

### Requirement: Inventory Management mounted as a custom addon
The Docker Compose configuration SHALL mount the `inventory_management` module directory into Odoo's custom addons path so it is discoverable without rebuilding the image.

#### Scenario: Module discoverable after startup
- **WHEN** the environment is running and the developer updates the Apps list in Odoo
- **THEN** "Inventory Management" appears as an installable module, reflecting the current state of the local `inventory_management` source directory

### Requirement: Documented verification steps
The README SHALL document how to start the environment, log into Odoo, and install the Inventory Management module to verify it loads without errors.

#### Scenario: Following the README from a clean clone
- **WHEN** a developer with only Docker installed follows the README's Docker section
- **THEN** they can start Odoo, log in, and install Inventory Management successfully using only those instructions
