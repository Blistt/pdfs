import unittest
from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    def test_preview_precedes_download_and_uses_identical_bytes_after_editing(self):
        with patch("streamlit.pdf", wraps=st.pdf) as preview, \
             patch("streamlit.download_button", wraps=st.download_button) as download:
            app = AppTest.from_file(str(APP)).run(timeout=30)
            self.assertFalse(app.exception)
            first_pdf = preview.call_args.args[0]
            self.assertEqual(first_pdf, download.call_args.kwargs["data"])
            elements = [element.type for element in app.main]
            self.assertLess(elements.index("bidi_component"), elements.index("download_button"))
            self.assertEqual(download.call_args.kwargs["label"], "Descargar PDF")

            app.text_input[0].set_value("Constancia de prueba actualizada")
            app.text_area[0].set_value("Nuevo contenido para María Muñoz: <texto literal> & prueba.")
            app.run(timeout=30)
            self.assertFalse(app.exception)
            new_pdf = preview.call_args.args[0]
            self.assertNotEqual(first_pdf, new_pdf)
            self.assertEqual(new_pdf, download.call_args.kwargs["data"])

    def test_invalid_edit_removes_old_preview_and_download_and_recovers(self):
        app = AppTest.from_file(str(APP)).run(timeout=30)
        app.text_input[0].set_value("Título excesivo " * 200).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.warning), 1)
        self.assertEqual(len(app.get("bidi_component")), 0)
        self.assertEqual(len(app.get("download_button")), 0)
        app.text_input[0].set_value("Constancia corregida").run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.warning)
        self.assertEqual(len(app.get("download_button")), 1)


if __name__ == "__main__":
    unittest.main()
