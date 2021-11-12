import pytest

from diot import Diot
from pipen import Proc, Pipen
from pipen_filters import PipenFilters

def test_plugin():
    pf = PipenFilters()
    config = Diot()
    pf.on_setup.impl(config)
    assert "template_opts" in config
    assert "filters" in config.template_opts
    assert "globals" in config.template_opts

def test_use_as_globals(tmp_path):
    outfile = tmp_path / 'test.txt'
    class P(Proc):
        input = "a"
        output = "out:var:{{stem(in.a)}}"
        script = f"echo {{{{out.out}}}} > {outfile}"

    Pipen().set_start(P).set_data(["a/b/c.txt"]).run()
    assert outfile.read_text().strip() == "c"
