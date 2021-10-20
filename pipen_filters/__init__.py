"""Add a set of useful filters for pipen templates"""

from typing import Any, Dict
from pipen import plugin

from .filters import FILTERS

__version__ = "0.0.2"


class PipenFilters:
    __version__: str = __version__

    @plugin.impl
    def on_setup(config: Dict[str, Any]) -> None:  # type: ignore
        """Add the filters"""
        if "template_opts" not in config:
            config.template_opts: Dict[str, Any] = {}

        if "filters" not in config.template_opts:
            config.template_opts.filters = {}

        config.template_opts.filters.update(FILTERS)
