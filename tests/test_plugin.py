import pytest

from pipen import Proc, Pipen
from pipen_filters import PipenFilters


@pytest.mark.asyncio
async def test_plugin():
    pf = PipenFilters()
    p = Pipen(plugins=["filters"])
    await pf.on_init.impl(p)
    assert "template_opts" in p.config
    assert "filters" in p.config.template_opts
    assert "globals" in p.config.template_opts


def test_use_as_globals(tmp_path):
    outfile = tmp_path / "test.txt"

    class P(Proc):
        input = "a"
        output = "out:var:{{stem(in.a)}}"
        script = f"echo {{{{out.out}}}} > {outfile}"

    Pipen(plugins=["filters"]).set_start(P).set_data(["a/b/c.txt"]).run()
    assert outfile.read_text().strip() == "c"
