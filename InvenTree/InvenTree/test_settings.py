"""Test settings for running benchmark tests with pytest."""

import os

os.environ.setdefault('TESTING', '1')
from .settings import *  # noqa

Q_CLUSTER['workers'] = 0
Q_CLUSTER['sync'] = True
