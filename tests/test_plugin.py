import pytest

from diot import Diot
from pipen_filters import PipenFilters

def test_plugin():
    pf = PipenFilters()
    config = Diot()
    pf.on_setup.impl(config)
    assert "template_opts" in config
    assert "filters" in config.template_opts
