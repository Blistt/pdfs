"""Lay out printable letters with bounded text and embedded local fonts."""

import io
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether, PageTemplate,
    Paragraph, Spacer,
)

PAGE_W, PAGE_H = letter
LEFT, RIGHT, TOP, BOTTOM = 60, PAGE_W - 60, PAGE_H - 45, 45
BOX_TOP, BOX_BOTTOM = TOP - 93, BOTTOM + 40
TEXT_LEFT, TEXT_WIDTH = LEFT + 15, RIGHT - LEFT - 30
TEXT_TOP, TEXT_BOTTOM = BOX_TOP - 36, BOX_BOTTOM + 26
TEXT_HEIGHT = TEXT_TOP - TEXT_BOTTOM
TITLE_WIDTH, TITLE_HEIGHT = RIGHT - 150 - 20 - LEFT, 75
BODY_MAX_SIZE, BODY_MIN_SIZE = 12, 10
TITLE_MAX_SIZE, TITLE_MIN_SIZE = 18, 10

TEAL, PINK, DARK = map(HexColor, ("#2abfbf", "#e84393", "#2d3436"))
APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = str(APP_DIR / "logo.jpeg")
FONT, FONT_BOLD = "Caladea", "Caladea-Bold"
for name, filename in ((FONT, "Caladea-Regular.ttf"), (FONT_BOLD, "Caladea-Bold.ttf")):
    pdfmetrics.registerFont(TTFont(name, str(APP_DIR / "fonts" / filename)))


class LetterLayoutError(ValueError):
    """The supplied text cannot fit at a readable size."""


@dataclass(frozen=True)
class GeneratedPDF:
    data: bytes
    page_count: int
    body_font_size: float
    title_font_size: float


def _sizes(maximum, minimum):
    """Try the largest readable size first, in quarter-point steps."""
    return (step / 4 for step in range(int(maximum * 4), int(minimum * 4) - 1, -1))


def _paragraph(text, size, *, bold=False, leading=None):
    # User text is literal, never ReportLab markup (including <, > and &).
    markup = escape(text).replace("\n", "<br/>") or "<br/>"
    return Paragraph(markup, ParagraphStyle(
        "letter", fontName=FONT_BOLD if bold else FONT, fontSize=size,
        leading=leading or size * 4 / 3, textColor=DARK,
        splitLongWords=True, allowWidows=False, allowOrphans=False,
    ))


def _fit_title(title):
    for size in _sizes(TITLE_MAX_SIZE, TITLE_MIN_SIZE):
        paragraph = _paragraph(title.strip(), size, bold=True, leading=size * 1.2)
        _, height = paragraph.wrap(TITLE_WIDTH, TITLE_HEIGHT)
        if height <= TITLE_HEIGHT:
            return paragraph, height, size
    raise LetterLayoutError(
        "El título es demasiado largo para el encabezado. Acórtalo un poco."
    )


def _content(size, cuerpo, ciudad, fecha, nombre_firma, cargo_firma,
             org_firma, email, celular, direccion):
    scale = size / BODY_MAX_SIZE
    body = [_paragraph("A quien corresponda:", size), Spacer(1, 6 * scale)]
    for line in cuerpo.strip().splitlines():
        if line.strip():
            body.extend([_paragraph(line.strip(), size), Spacer(1, 6 * scale)])
        else:
            body.append(Spacer(1, 6 * scale))

    # Keep the date, signature and contact details together on the last page.
    closing = []
    if ciudad.strip() and fecha.strip():
        closing.extend([
            _paragraph(
                "Se extiende la presente constancia a petición de la parte "
                "interesada y para los fines que a la misma convengan, "
                f"en {ciudad.strip()} a {fecha.strip()}.", size,
            ),
            Spacer(1, 6 * scale),
        ])
    closing.extend([
        Spacer(1, 18 * scale),
        _paragraph("Atentamente:", size),
        Spacer(1, 42),  # Leave physical room for a handwritten signature.
        HRFlowable(width="60%", thickness=0.75, color=DARK, hAlign="LEFT"),
        Spacer(1, 8 * scale),
    ])
    for value, bold in ((nombre_firma, True), (cargo_firma, False), (org_firma, True)):
        if value.strip():
            closing.append(_paragraph(value.strip(), size, bold=bold))
    closing.append(Spacer(1, 12 * scale))
    for label, value in (("Email", email), ("Cel", celular), ("Dirección", direccion)):
        if value.strip():
            paragraph = _paragraph(f"{label}: {value.strip()}", 11 * scale)
            if label == "Email":
                paragraph = Paragraph(
                    f'Email: <font color="#0000EE"><u>{escape(value.strip())}</u></font>',
                    paragraph.style,
                )
            closing.append(paragraph)
    return body, closing


def _height(flowables):
    return sum(item.wrap(TEXT_WIDTH, TEXT_HEIGHT)[1] for item in flowables)


def _build(title, title_paragraph, title_height, body, closing):
    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=letter, title=title, author="Concertinos")

    def draw_page(canvas, document):
        canvas.saveState()
        canvas.drawImage(LOGO_PATH, RIGHT - 150, TOP - 75, width=150, height=90,
                         preserveAspectRatio=True, mask="auto")
        title_paragraph.drawOn(canvas, LEFT, TOP - (TITLE_HEIGHT + title_height) / 2)
        canvas.setStrokeColor(HexColor("#cccccc"))
        canvas.setLineWidth(0.75)
        canvas.rect(LEFT - 5, BOX_BOTTOM, RIGHT - LEFT + 10, BOX_TOP - BOX_BOTTOM)
        for x, color in ((LEFT - 5, TEAL), (RIGHT + 5, PINK)):
            canvas.setFillColor(color)
            for y in (BOX_TOP, BOX_BOTTOM):
                canvas.rect(x - 7, y - 7, 14, 14, fill=1, stroke=0)
        if document.page > 1:
            canvas.setFillColor(DARK)
            canvas.setFont(FONT, 9)
            canvas.drawRightString(RIGHT, BOTTOM, f"Página {document.page}")
        canvas.restoreState()

    frame = Frame(TEXT_LEFT, TEXT_BOTTOM, TEXT_WIDTH, TEXT_HEIGHT,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="letter", frames=[frame], onPage=draw_page))
    doc.build([*body, KeepTogether(closing)])
    return buffer.getvalue(), doc.page


def generate_pdf(titulo, cuerpo, ciudad, fecha, nombre_firma, cargo_firma,
                 org_firma, email, celular, direccion):
    """Fit on one page when readable; use at most two pages without clipping."""
    title_paragraph, title_height, title_size = _fit_title(titulo)
    fields = (cuerpo, ciudad, fecha, nombre_firma, cargo_firma,
              org_firma, email, celular, direccion)

    for page_limit in (1, 2):
        for size in _sizes(BODY_MAX_SIZE, BODY_MIN_SIZE):
            body, closing = _content(size, *fields)
            # The closing block must fit on one page, even in a two-page letter.
            if _height(closing) > TEXT_HEIGHT:
                continue
            if _height(body) + _height(closing) > TEXT_HEIGHT * page_limit:
                continue
            data, page_count = _build(titulo, title_paragraph, title_height, body, closing)
            # Check actual pagination, including kept-together blocks and widows.
            if page_count <= page_limit:
                return GeneratedPDF(data, page_count, size, title_size)

    raise LetterLayoutError(
        "El texto no cabe en dos páginas con un tamaño legible. "
        "Acorta el cuerpo de la carta o los datos de firma y contacto."
    )
