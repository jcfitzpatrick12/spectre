# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# --------------------------------- # 
# Base stage.
# --------------------------------- # 
FROM python:3.10-slim AS base

# Set a default working directory for each stage.
WORKDIR /app

# Explictly set the user to root by default for each stage.
USER root

# --------------------------------- # 
# Build stage.
# --------------------------------- # 
FROM base AS build

# Copy in the build requirements, and the CLI application code.
COPY src pyproject.toml ./

# Install the build dependencies and CLI application system-wide.
RUN pip install .

# --------------------------------- # 
# Runtime stage.
# --------------------------------- # 
FROM base AS runtime

LABEL maintainer="Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>" \
      version="0.0.14" \
      description="Docker image for running the `spectre-cli`." \
      license="GPL-3.0-or-later"


WORKDIR /app

# Copy in the system-wide packages, and the CLI application executable.
COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build /usr/local/bin/spectre /usr/local/bin/spectre

# Create an arbitrary group and non-root user to run the application.
RUN groupadd --gid 1000 appgroup && \
    useradd -u 1000 -g appgroup appuser

# Change ownership of the application directory to the non-root user.
RUN chown -R appuser:appgroup /app

# Switch to the non-root user, to improve security.
USER appuser

# --------------------------------- # 
# Development stage.
# --------------------------------- # 
FROM base AS development

# Install development tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim && \  
    rm -rf /var/lib/apt/lists/*

# Clone the `spectre` repository and install the CLI in editable mode.
RUN git clone https://github.com/jcfitzpatrick12/spectre.git --no-checkout && cd spectre && \
    git sparse-checkout init --no-cone && \
    git sparse-checkout set cli/ && \
    git checkout && \
    pip install -e cli/

