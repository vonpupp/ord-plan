# Test GitHub Actions environment locally
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Install pipx (required for Poetry and Nox)
RUN python -m pip install --user pipx
RUN python -m pipx ensurepath

ENV PATH="/root/.local/bin:$PATH"

# Install tools with constraints (mimic GitHub Actions exactly)
WORKDIR /workspace
COPY .github/workflows/constraints.txt /tmp/constraints.txt
RUN pipx install --pip-args=--constraint=/tmp/constraints.txt poetry
RUN pipx install --pip-args=--constraint=/tmp/constraints.txt nox
RUN pipx inject --pip-args=--constraint=/tmp/constraints.txt nox nox-poetry

# Verify installations
RUN poetry --version
RUN poetry config installer.parallel false || true
RUN poetry self add poetry-plugin-export
RUN nox --version

# Copy project
COPY . /workspace

WORKDIR /workspace

# Default command: run same session as GitHub Actions
CMD ["nox", "--python=3.10", "-s", "tests"]
