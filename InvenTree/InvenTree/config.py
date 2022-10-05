"""Helper functions for loading InvenTree configuration options."""

import logging
from pathlib import Path

from accu.accu.core.config import get_setting, get_settings_dir
from accu.accu.core.utils import is_true

logger = logging.getLogger('inventree')


def get_base_dir() -> Path:
    """Returns the base (top-level) InvenTree directory."""
    return Path(__file__).parent.parent.resolve()


def get_boolean_setting(env_var=None, config_key=None, default_value=False):
    """Helper function for retreiving a boolean configuration setting"""

    return is_true(get_setting(env_var, config_key, default_value))


def get_media_dir(create=True):
    """Return the absolute path for the 'media' directory (where uploaded files are stored)"""
    return get_settings_dir('media', create=create)


def get_static_dir(create=True):
    """Return the absolute path for the 'static' directory (where static files are stored)"""
    return get_settings_dir('media', create=create)
