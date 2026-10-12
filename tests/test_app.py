from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_interactive_budget_and_portfolio():
    app=AppTest.from_file(str(Path(__file__).parents[1]/'app.py'),default_timeout=45).run()
    assert not app.exception
    assert any(m.value=='-1,68 milyar TL' for m in app.metric)
    app.slider(key='bia_delay').set_value(2).run()
    assert not app.exception
    assert any(m.value=='0,62 milyar TL' for m in app.metric)
    app.slider(key='port_budget').set_value(0.).run()
    app.checkbox(key='port_floor').check().run()
    assert not app.exception
    assert any('uygun portföy yok' in x.value for x in app.warning)
