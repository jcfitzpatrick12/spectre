"""Configure environment variables for the CLI"""

import os

SPECTRE_SERVICE_HOST = os.environ.get("SPECTRE_SERVICE_HOST", None)
SPECTRE_SERVICE_PORT = os.environ.get("SPECTRE_SERVICE_PORT", None)

if SPECTRE_SERVICE_HOST is not None and SPECTRE_SERVICE_PORT is not None:
    SPECTRE_SERVER = f"http://{SPECTRE_SERVICE_HOST}:{SPECTRE_SERVICE_PORT}"
else:
    SPECTRE_SERVER       = os.environ.get("SPECTRE_SERVER", "http://localhost:5000")


