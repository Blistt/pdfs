#!/usr/bin/env python3
"""
Genera una constancia estudiantil PDF con el formato de Concertinos.

Uso:
    python3 generar_constancia.py

Produce: constancia-jennifer.pdf
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "constancia-jennifer-generated.pdf")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.jpeg")

PAGE_W, PAGE_H = letter  # 612 x 792 pts

# Margins
LEFT = 60
RIGHT = PAGE_W - 60
TOP = PAGE_H - 45
BOTTOM = 45

# Colors (sampled from the original)
TEAL = HexColor("#2abfbf")       # cyan/teal accent bar & bottom-left square
PINK = HexColor("#e84393")       # pink/magenta bottom-right square
DARK = HexColor("#2d3436")       # dark text color
LINK_BLUE = HexColor("#0000EE")  # hyperlink color

# Fonts – Caladea is a metric-compatible Cambria replacement
FONT_DIR = "/usr/share/fonts/truetype/crosextra"
pdfmetrics.registerFont(TTFont("Cambria", f"{FONT_DIR}/Caladea-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Cambria-Bold", f"{FONT_DIR}/Caladea-Bold.ttf"))

FONT = "Cambria"
FONT_BOLD = "Cambria-Bold"


def draw_pdf():
    c = canvas.Canvas(OUTPUT_FILE, pagesize=letter)
    c.setTitle("Constancia estudiantil")

    # ------------------------------------------------------------------
    # 1. LOGO (top-right)
    # ------------------------------------------------------------------
    logo = ImageReader(LOGO_PATH)
    logo_w = 150
    logo_h = 90
    logo_x = RIGHT - logo_w
    logo_y = TOP - logo_h + 15
    c.drawImage(LOGO_PATH, logo_x, logo_y, width=logo_w, height=logo_h,
                preserveAspectRatio=True, mask='auto')

    # ------------------------------------------------------------------
    # 2. TITLE "Constancia estudiantil" (top-left, bold)
    # ------------------------------------------------------------------
    c.setFont(FONT_BOLD, 18)
    c.setFillColor(DARK)
    title_y = TOP - 55
    c.drawString(LEFT, title_y, "Constancia estudiantil")

    # ------------------------------------------------------------------
    # 3. Content box (thin border)
    # ------------------------------------------------------------------
    box_top = title_y - 38
    box_bottom = BOTTOM + 40
    c.setStrokeColor(HexColor("#cccccc"))
    c.setLineWidth(0.75)
    c.rect(LEFT - 5, box_bottom, (RIGHT - LEFT + 10), box_top - box_bottom)

    # ------------------------------------------------------------------
    # 5. Body text
    # ------------------------------------------------------------------
    text_left = LEFT + 15
    text_right = RIGHT - 15
    text_width = text_right - text_left
    c.setFillColor(DARK)

    y = box_top - 80  # starting y for text

    # "A quien corresponda:"
    c.setFont(FONT, 12)
    y = draw_paragraph(c, "A quien corresponda:", text_left, y, text_width, 12, leading=16)

    # First paragraph
    para1 = (
        "Por medio de la presente se hace constar que la joven Aranza Banda Espino "
        "est\u00e1 inscrita en esta instituci\u00f3n, donde recibe apoyo "
        "para seguir desarrollando sus habilidades conductuales, cognitivas, "
        "emocionales y sociales, desde el a\u00f1o 2018 a la fecha; observando "
        "siempre una puntual asistencia y constancia en su desempe\u00f1o."
    )
    y -= 6
    y = draw_paragraph(c, para1, text_left, y, text_width, 12, leading=16)

    # Second paragraph
    para2 = (
        "Se extiende la presente constancia a petici\u00f3n de la parte interesada "
        "y para los fines que a la misma convengan, en Chihuahua, Chihuahua a "
        "los 16 d\u00edas del mes de Febrero del 2026."
    )
    y -= 6
    y = draw_paragraph(c, para2, text_left, y, text_width, 12, leading=16)

    # "Atentamente:"
    y -= 35
    c.setFont(FONT, 12)
    c.drawString(text_left, y, "Atentamente:")

    # ------------------------------------------------------------------
    # 6. Signature line
    # ------------------------------------------------------------------
    y -= 65
    sig_line_width = text_width * 0.6
    c.setStrokeColor(DARK)
    c.setLineWidth(0.75)
    c.line(text_left, y, text_left + sig_line_width, y)

    # ------------------------------------------------------------------
    # 7. Signer info
    # ------------------------------------------------------------------
    y -= 18
    c.setFont(FONT_BOLD, 12)
    c.drawString(text_left, y, "Lic. Isabel Pazos")

    y -= 16
    c.setFont(FONT, 12)
    c.drawString(text_left, y, "Directora")

    y -= 16
    c.setFont(FONT_BOLD, 12)
    c.drawString(text_left, y, "CONCERTINOS: Centro para personas con Diversidad Funcional")

    # Contact info
    y -= 22
    c.setFont(FONT, 11)

    # Email with hyperlink styling
    c.drawString(text_left, y, "Email: ")
    email_x = text_left + c.stringWidth("Email: ", FONT, 11)
    c.setFillColor(LINK_BLUE)
    c.drawString(email_x, y, "isabellpazos@gmail.com")
    # underline
    uw = c.stringWidth("isabellpazos@gmail.com", FONT, 11)
    c.setStrokeColor(LINK_BLUE)
    c.setLineWidth(0.5)
    c.line(email_x, y - 1.5, email_x + uw, y - 1.5)
    c.setFillColor(DARK)
    c.setStrokeColor(DARK)

    y -= 16
    c.drawString(text_left, y, "Cel: 614 1106956")

    y -= 16
    c.drawString(text_left, y, "Direcci\u00f3n: Calle Pino 607")

    # ------------------------------------------------------------------
    # 8. Colored squares at the 4 corners of the content box
    # ------------------------------------------------------------------
    sq = 14  # size of the small colored squares
    bx = LEFT - 5          # box left x
    bx2 = RIGHT + 5        # box right x

    # Top-left – teal
    c.setFillColor(TEAL)
    c.rect(bx - sq/2, box_top - sq/2, sq, sq, fill=1, stroke=0)

    # Top-right – pink
    c.setFillColor(PINK)
    c.rect(bx2 - sq/2, box_top - sq/2, sq, sq, fill=1, stroke=0)

    # Bottom-left – teal
    c.setFillColor(TEAL)
    c.rect(bx - sq/2, box_bottom - sq/2, sq, sq, fill=1, stroke=0)

    # Bottom-right – pink
    c.setFillColor(PINK)
    c.rect(bx2 - sq/2, box_bottom - sq/2, sq, sq, fill=1, stroke=0)

    # ------------------------------------------------------------------
    c.save()
    print(f"PDF generated: {OUTPUT_FILE}")


def draw_paragraph(c, text, x, y, max_width, font_size, leading=14, font_name=None):
    if font_name is None:
        font_name = FONT
    """Simple word-wrap paragraph drawer. Returns the y after the last line."""
    c.setFont(font_name, font_size)
    words = text.split()
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, font_name, font_size) <= max_width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


if __name__ == "__main__":
    draw_pdf()
