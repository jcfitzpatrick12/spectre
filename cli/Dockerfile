FROM python:3.10-slim

WORKDIR /app

# Copy in the spectre-cli program, along with the build requirements.
COPY src pyproject.toml ./

# Install the dependencies system-wide.
RUN pip install .

