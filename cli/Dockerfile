# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# --------------------------------- # 
# Create the base stage
# --------------------------------- # 
FROM python:3.10-slim AS base

WORKDIR /app

# Copy in the spectre-cli program, along with the build requirements.
COPY src pyproject.toml ./

# Install the dependencies system-wide.
RUN pip install .

# --------------------------------- # 
# Create the final runtime image
# --------------------------------- # 
FROM python:3.10-slim AS runtime

WORKDIR /app

# Copy in system-wide python packages for the cli
COPY --from=base /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=base /usr/local/bin/spectre /usr/local/bin/spectre

# --------------------------------- # 
# Create the development stage
# --------------------------------- # 
FROM python:3.10-slim AS development

RUN apt-get update && \
    apt-get install -y \
    # Install development tools.
    git python3-pip vim 

WORKDIR /app

# Clone then install the latest `spectre` code, ready for development.
COPY --chmod=0755 scripts/bash/install_spectre_latest.sh ./install_spectre_latest.sh
RUN ./install_spectre_latest.sh && rm ./install_spectre_latest.sh

CMD ["/bin/bash"]

