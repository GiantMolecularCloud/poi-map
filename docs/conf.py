"""Sphinx configuration."""

import os
import sys
import datetime

today = datetime.date.today()

sys.path.insert(0, os.path.abspath("../poi_map"))

project = "poi-map"
author = "giantmolecularcloud"
copyright = f"{today.year} {author}"
release = "1.2.0"

html_theme_options = {"body_max_width": "80%"}
html_theme = "sphinx_rtd_theme"

extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.coverage",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "sphinx_autodoc_typehints",
    "sphinxarg.ext",
    "sphinxcontrib.autodoc_pydantic",
]
autosummary_generate = True
autoclass_content = "both"

autoapi_type = "python"
autoapi_dirs = ["../poi_map"]

todo_include_todos = True
coverage_show_missing_items = True
autodoc_pydantic_model_show_json = True
autodoc_pydantic_settings_show_json = True
