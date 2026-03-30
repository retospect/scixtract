"""scixtract — DEPRECATED. Use acatome-extract instead."""

import warnings

__version__ = "2.0.0"

warnings.warn(
    "scixtract is deprecated. Use acatome-extract instead: pip install acatome-extract",
    DeprecationWarning,
    stacklevel=2,
)
