import os
import sys

from streamlit.web import cli


def app():
    sys.argv = ["streamlit", "run", "src/pdfchat_app/app.py"]
    cli.main()
