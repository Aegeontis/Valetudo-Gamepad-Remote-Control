# Valetudo-Gamepad-Remote-Control

Drive a Valetudo-enabled robot vacuum with a gamepad via pygame.

## Attribution

This was **vibe-coded with an LLM**. It is a Python port and extension of two existing gists:

- Main source: <https://gist.github.com/Depau/904ce14b04d935b6f9829cdf2cda64f3>
- A bit of: <https://gist.github.com/Hypfer/fcfa39996bd7522bbe2c5f18acb1fcf4>

**Tested only on a Dreame L10s Ultra running Valetudo 2026.08.0.** Other robot models or Valetudo versions may behave differently — especially the velocity/angle semantics of `HighResolutionManualControlCapability`, which vary by vendor.

## Requirements

- Python 3.10+
- A Valetudo-enabled robot with `HighResolutionManualControlCapability`
- A gamepad recognized by SDL2

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame-ce requests

export VALE_URL="http://your-valetudo-host"
python3 main.py
```

## Controls

| Input | Action |
|---|---|
| Left stick vertical axis | Forward / backward |
| Left stick horizontal axis | Steer left / right |
| X button | Stop robot (abort current action) |
| Y button | Send robot home |

## Notes

- `verify=False` is set on all requests to allow using self-signed certificates.
- Commands are sent at most every 150 ms while moving; at rest, only one stop command is sent.
- The HTTP worker uses a size-1 queue that drops stale commands, so a slow robot won't cause pileup.

## Files

- `main.py` — pygame loop, joystick → velocity/angle mapping
- `vale.py` — Valetudo API client
