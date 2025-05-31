"""Configure environment variables."""

import os

SPECTRE_BIND_HOST = os.environ.get("SPECTRE_BIND_HOST", "0.0.0.0")
SPECTRE_BIND_PORT = int(os.environ.get("SPECTRE_BIND_PORT", "5000"))
