"""Add a set of useful filters for pipen templates"""
import logging
from typing import TYPE_CHECKING

from pipen import plugin
from pipen.utils import logger

from .filters import FILTERS

if TYPE_CHECKING:  # pragma: no cover
    from pipen import Pipen

__version__ = "1.1.0"


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


class TemplateOptsShortenFilter(logging.Filter):
    """Shorten the template opts in the log"""

    def filter(self, record: logging.LogRecord) -> bool:
        if (
            record.msg == "[bold][magenta]%-16s:[/magenta][/bold] %s"
            and isinstance(record.args, tuple)
            and len(record.args) == 2
            and (
                record.args[0] == "template_opts"
                or (
                    not record.args[0]
                    and (
                        isinstance(record.args[1], str)
                        and record.args[1][:8] in ("filters=", "globals=")
                    )
                )
            )
        ):
            record.msg = "[bold][magenta]%-16s:[/magenta][/bold] %.54s..."
        return True


logger.logger.addFilter(TemplateOptsShortenFilter())
