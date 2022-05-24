"""Add a set of useful filters for pipen templates"""

from typing import TYPE_CHECKING
from pipen import plugin

from .filters import FILTERS

if TYPE_CHECKING:  # pragma: no cover
    from pipen import Pipen

__version__ = "0.1.2"


class PipenFilters:
    __version__: str = __version__

    @plugin.impl
    async def on_init(pipen: "Pipen") -> None:  # type: ignore
        """Add the filters"""
        config = pipen.config
        if "template_opts" not in config:  # pragma: no cover
            config.template_opts = {}

        if "filters" not in config.template_opts:
            config.template_opts.filters = {}
        if "globals" not in config.template_opts:
            config.template_opts.globals = {}

        config.template_opts.filters = {
            **FILTERS,
            **config.template_opts.filters,
        }
        config.template_opts.globals = {
            **FILTERS,
            **config.template_opts.globals,
        }
