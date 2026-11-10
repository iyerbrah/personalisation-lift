"""All three pages of the Streamlit app render from the committed results without errors."""
import pytest
from streamlit.testing.v1 import AppTest

from conftest import ROOT

PAGES = {"views/lift.py": "Recommender engagement experiment", "views/who_benefits.py": "Who benefits",
         "views/why.py": "Popularity or fit"}


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    if page != "views/lift.py":
        at.switch_page(page).run()
    assert not at.exception
    assert at.title[0].value == PAGES[page]
