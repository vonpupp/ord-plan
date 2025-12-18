"""Sphinx configuration."""

project = "ORD Plan"
author = "vonpupp"
copyright = "2025, vonpupp"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
