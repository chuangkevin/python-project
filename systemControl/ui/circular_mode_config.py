"""Helper to load and validate the circular screen mode configuration.

This module provides a thin wrapper around the JSON config file so UI
components can request mode descriptions in a stable format.
"""
import json
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent.parent / "config" / "circular_modes.json"

def load_config() -> Dict[str, Any]:
    """Load and return the circular modes config.

    Returns a dictionary with at least a top-level "modes" key.
    Raises FileNotFoundError or JSONDecodeError on failure.
    """
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Basic validation
    if 'modes' not in data or not isinstance(data['modes'], dict):
        raise ValueError('circular_modes.json missing top-level "modes" mapping')

    return data


def get_mode(mode_id: str) -> Dict[str, Any]:
    cfg = load_config()
    mode = cfg['modes'].get(mode_id)
    if mode is None:
        raise KeyError(f"Mode '{mode_id}' not found in circular_modes.json")
    return mode
