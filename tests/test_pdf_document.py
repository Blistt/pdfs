import unittest
from io import BytesIO

from pypdf import PdfReader

from pdf_document import BODY_MIN_SIZE, LetterLayoutError, generate_pdf


BODY = (
    "Por medio de la presente se hace constar que María Muñoz está inscrita en "
    "esta institución, donde recibe apoyo para seguir desarrollando sus "
    "habilidades conductuales, cognitivas, emocionales y sociales."
)
SAMPLE = dict(
    titulo="Constancia estudiantil", cuerpo=BODY,
    ciudad="Chihuahua, Chihuahua", fecha="los 9 días de septiembre del 2026",
    nombre_firma="Lic. Isabel Pazos", cargo_firma="Directora",
    org_firma="CONCERTINOS: Centro para personas con Diversidad Funcional",
    email="ejemplo@example.com", celular="614 000 0000", direccion="Calle Pino 607",
)


def compact(text):
    return "".join(text.split())


class LetterTests(unittest.TestCase):
    def make_letter(self, **changes):
        result = generate_pdf(**(SAMPLE | changes))
        reader = PdfReader(BytesIO(result.data))
        self.assertEqual(len(reader.pages), result.page_count)
        return result, reader

    def test_short_letter_keeps_normal_font_and_embeds_both_fonts(self):
        result, reader = self.make_letter()
        self.assertEqual((result.page_count, result.body_font_size, result.title_font_size), (1, 12, 18))
        self.assertIn(compact(BODY), compact(reader.pages[0].extract_text()))
        self.assertIn(b"Caladea-Regular", result.data)
        self.assertIn(b"Caladea-Bold", result.data)
        self.assertIn(b"/FontFile2", result.data)

    def test_long_title_scales_and_retains_every_word(self):
        title = (
            "Constancia de inscripción, asistencia y participación en el programa "
            "de acompañamiento educativo y desarrollo integral para personas con diversidad funcional"
        )
        result, reader = self.make_letter(titulo=title)
        self.assertLess(result.title_font_size, 18)
        self.assertGreaterEqual(result.title_font_size, 10)
        self.assertEqual(result.page_count, 1)
        self.assertIn(compact(title), compact(reader.pages[0].extract_text()))

    def test_long_body_shrinks_to_fit_one_page(self):
        body = "\n\n".join([BODY] * 7)
        result, reader = self.make_letter(cuerpo=body)
        self.assertEqual(result.page_count, 1)
        self.assertLess(result.body_font_size, 12)
        self.assertGreaterEqual(result.body_font_size, BODY_MIN_SIZE)
        self.assertEqual(compact(reader.pages[0].extract_text()).count(compact(BODY)), 7)

    def test_two_pages_keep_all_text_and_the_closing_together(self):
        result, reader = self.make_letter(cuerpo="\n\n".join([BODY] * 12))
        self.assertEqual(result.page_count, 2)
        self.assertGreaterEqual(result.body_font_size, BODY_MIN_SIZE)
        pages = [page.extract_text() for page in reader.pages]
        self.assertEqual(compact("".join(pages)).count(compact(BODY)), 12)
        self.assertNotIn("Atentamente:", pages[0])
        for text in ("Se extiende", "Atentamente:", SAMPLE["nombre_firma"], SAMPLE["email"]):
            self.assertIn(text, pages[1])

    def test_unbroken_tokens_and_literal_markup_are_not_lost(self):
        body = "ÁÉÍÓÚ áéíóú ñ ü <b>literal</b> & 2 < 3 > 1\n" + "W" * 300
        _, reader = self.make_letter(cuerpo=body, email="correo&prueba@example.com")
        text = compact("".join(page.extract_text() for page in reader.pages))
        self.assertIn(compact(body), text)
        self.assertIn("correo&prueba@example.com", text)

    def test_long_signature_and_contact_fields_wrap(self):
        changes = dict(nombre_firma="Nombre de prueba " * 5, org_firma="Organización educativa " * 8,
                       direccion="Dirección de prueba " * 8, email="x" * 100 + "@example.com")
        result, reader = self.make_letter(**changes)
        self.assertLessEqual(result.page_count, 2)
        text = compact("".join(page.extract_text() for page in reader.pages))
        for value in changes.values():
            self.assertIn(compact(value), text)

    def test_blank_fields_still_make_a_valid_letter(self):
        result, _ = self.make_letter(**dict.fromkeys(SAMPLE, ""))
        self.assertEqual(result.page_count, 1)

    def test_excessive_text_reports_a_limit_instead_of_clipping(self):
        for changes in (dict(cuerpo=BODY * 100), dict(titulo="Título largo " * 100),
                        dict(org_firma="Organización " * 300)):
            with self.subTest(changes=list(changes)), self.assertRaises(LetterLayoutError):
                self.make_letter(**changes)


if __name__ == "__main__":
    unittest.main()
