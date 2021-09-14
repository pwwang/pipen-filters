"""Add a set of useful filters for pipen templates"""

from typing import Any, Dict
from pipen import plugin

from .filters import FILTERS

__version__ = "0.0.1"


class PipenFilters:
    __version__: str = __version__

    @plugin.impl
    def on_setup(config: Dict[str, Any]) -> None:
        """Add the filters"""
        if "template_opts" not in config:
            config.template_opts = {}

        if "filters" not in config.template_opts:
            config.template_opts.filters = {}

        config.template_opts.filters.update(FILTERS)
