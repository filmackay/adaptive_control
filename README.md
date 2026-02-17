# Adaptive Control

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

**Adaptive Model Predictive Control (MPC)** for Home Assistant. Learn your system's dead-time and gain automatically.

> "Point it at a sensor, give it a target, and let it figure out the rest."

## Key Features

*   **Self-Learning (RLS):** Automatically finds the system gain (e.g., Amps to Watts) and dead-time (delay). No manual PID tuning required.
*   **Adaptive:** Adjusts to changing conditions (e.g., voltage drop, resistance changes).
*   **Grid Zero:** Perfect for Solar Diversion (EV Charging, Hot Water) to keep grid import at 0.

## How it Works

Unlike a PID controller which reacts to error, this controller builds an internal mathematical model of your system's response (Impulse Response) and uses it to predict the optimal control output.

See the [Design Documentation](docs/design.md) for a deep dive into the math.

## Installation

1.  Open HACS.
2.  Add this repository as a **Custom Repository**.
3.  Search for "Adaptive Control" and install.
4.  Restart Home Assistant.

## Configuration

1.  Go to **Settings > Devices & Services**.
2.  Click **Add Integration**.
3.  Search for **Adaptive Control**.
4.  Follow the setup wizard:
    *   **Name:** e.g., "EV Solar Charger"
    *   **Input Sensor:** e.g., `sensor.grid_power` (Active Power)
    *   **Output Entity:** e.g., `number.charger_limit`
    *   **Target:** `0` (Watts)

## Platforms

This integration provides:
*   **Switch:** Enable/Disable the control loop.
*   **Sensor:** The calculated control output and diagnostic metrics (Gain, Error).
*   **Services:** `adaptive_control.update` (for advanced manual triggering).

## Development

This project is configured for **VS Code Devcontainers**.

1.  Open the project in VS Code.
2.  Click **"Reopen in Container"** when prompted (or use `Cmd+Shift+P` > *Dev Containers: Reopen in Container*).
3.  Wait for the container to build.

### Running Locally

**Start Home Assistant:**
```bash
scripts/develop
```

**Run Tests:**
```bash
uv run pytest
```

**Verify Logic:**
The core math is in `custom_components/adaptive_control/adaptive_logic.py`.
Unit tests are in `tests/test_adaptive_logic.py`.
