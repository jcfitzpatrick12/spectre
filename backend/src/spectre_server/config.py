"""Configure environment variables."""

import os

SPECTRE_SERVICE_HOST  = os.environ.get("SPECTRE_SERVICE_HOST", "0.0.0.0")
SPECTRE_SERVICE_PORT  = int( os.environ.get("SPECTRE_SERVICE_PORT", "5000") )
