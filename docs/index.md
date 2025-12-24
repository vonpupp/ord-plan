## 🚀 Installation

### Method 1: uv (Recommended)

[uv](https://docs.astral.sh/uv/) is modern, fast Python package installer:

```console
# Install as a system tool (recommended for most users)
$ uv tool install ord-plan
```

### Method 2: pip

Traditional installation using pip:

```console
# Install from PyPI
$ pip install ord-plan

# Or install with user permissions only
$ pip install --user ord-plan
```

### Development Installation (Editable)

For contributors who want to modify the code:

#### Using uv

```console
# Clone repository
$ git clone https://github.com/vonpupp/ord-plan.git
$ cd ord-plan

# Install in editable mode for development
$ uv pip install -e .
```

#### Using pip

```console
# Clone repository
$ git clone https://github.com/vonpupp/ord-plan.git
$ cd ord-plan

# Create and activate virtual environment (optional but recommended)
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
$ pip install -e .
```
