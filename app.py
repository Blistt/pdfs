import io
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# PDF constants
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = letter
LEFT = 60
RIGHT = PAGE_W - 60
TOP = PAGE_H - 45
BOTTOM = 45

TEAL = HexColor("#2abfbf")
PINK = HexColor("#e84393")
DARK = HexColor("#2d3436")
LINK_BLUE = HexColor("#0000EE")

FONT_DIR = "/usr/share/fonts/truetype/crosextra"
pdfmetrics.registerFont(TTFont("Cambria", f"{FONT_DIR}/Caladea-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Cambria-Bold", f"{FONT_DIR}/Caladea-Bold.ttf"))
FONT = "Cambria"
FONT_BOLD = "Cambria-Bold"

LOGO_PATH = "logo.jpeg"


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------
def draw_paragraph(c, text, x, y, max_width, font_size, leading=16, font_name=None):
    if font_name is None:
        font_name = FONT
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


def generate_pdf(titulo, cuerpo, ciudad, fecha, nombre_firma, cargo_firma,
                 org_firma, email, celular, direccion):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle(titulo)

    # 1. Logo
    c.drawImage(LOGO_PATH, RIGHT - 150, TOP - 90 + 15, width=150, height=90,
                preserveAspectRatio=True, mask='auto')

    # 2. Title
    c.setFont(FONT_BOLD, 18)
    c.setFillColor(DARK)
    title_y = TOP - 55
    c.drawString(LEFT, title_y, titulo)

    # 3. Content box
    box_top = title_y - 38
    box_bottom = BOTTOM + 40
    c.setStrokeColor(HexColor("#cccccc"))
    c.setLineWidth(0.75)
    c.rect(LEFT - 5, box_bottom, (RIGHT - LEFT + 10), box_top - box_bottom)

    # 4. Body text
    text_left = LEFT + 15
    text_right = RIGHT - 15
    text_width = text_right - text_left
    c.setFillColor(DARK)

    y = box_top - 80

    # Greeting
    c.setFont(FONT, 12)
    y = draw_paragraph(c, "A quien corresponda:", text_left, y, text_width, 12)

    # Body paragraphs
    for para in cuerpo.strip().split("\n"):
        para = para.strip()
        if not para:
            y -= 6
            continue
        y -= 6
        y = draw_paragraph(c, para, text_left, y, text_width, 12)

    # Location + date line
    if ciudad and fecha:
        linea_lugar = f"Se extiende la presente constancia a petici\u00f3n de la parte interesada y para los fines que a la misma convengan, en {ciudad} a {fecha}."
        y -= 6
        y = draw_paragraph(c, linea_lugar, text_left, y, text_width, 12)

    # Atentamente
    y -= 35
    c.setFont(FONT, 12)
    c.drawString(text_left, y, "Atentamente:")

    # Signature line
    y -= 65
    sig_line_width = text_width * 0.6
    c.setStrokeColor(DARK)
    c.setLineWidth(0.75)
    c.line(text_left, y, text_left + sig_line_width, y)

    # Signer info
    y -= 18
    c.setFont(FONT_BOLD, 12)
    c.drawString(text_left, y, nombre_firma)

    y -= 16
    c.setFont(FONT, 12)
    c.drawString(text_left, y, cargo_firma)

    y -= 16
    c.setFont(FONT_BOLD, 12)
    c.drawString(text_left, y, org_firma)

    # Contact
    y -= 22
    c.setFont(FONT, 11)

    if email:
        c.drawString(text_left, y, "Email: ")
        email_x = text_left + c.stringWidth("Email: ", FONT, 11)
        c.setFillColor(LINK_BLUE)
        c.drawString(email_x, y, email)
        uw = c.stringWidth(email, FONT, 11)
        c.setStrokeColor(LINK_BLUE)
        c.setLineWidth(0.5)
        c.line(email_x, y - 1.5, email_x + uw, y - 1.5)
        c.setFillColor(DARK)
        c.setStrokeColor(DARK)
        y -= 16

    if celular:
        c.drawString(text_left, y, f"Cel: {celular}")
        y -= 16

    if direccion:
        c.drawString(text_left, y, f"Direcci\u00f3n: {direccion}")

    # Corner squares
    sq = 14
    bx = LEFT - 5
    bx2 = RIGHT + 5

    c.setFillColor(TEAL)
    c.rect(bx - sq/2, box_top - sq/2, sq, sq, fill=1, stroke=0)
    c.setFillColor(PINK)
    c.rect(bx2 - sq/2, box_top - sq/2, sq, sq, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(bx - sq/2, box_bottom - sq/2, sq, sq, fill=1, stroke=0)
    c.setFillColor(PINK)
    c.rect(bx2 - sq/2, box_bottom - sq/2, sq, sq, fill=1, stroke=0)

    c.save()
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Generador de Constancias - Concertinos", page_icon=":page_facing_up:")
st.image(LOGO_PATH, width=200)
st.title("Generador de Constancias")
st.markdown("Llena los campos y descarga tu constancia en PDF.")

st.divider()

titulo = st.text_input("Titulo del documento", value="Constancia estudiantil")

cuerpo = st.text_area(
    "Cuerpo del documento",
    height=150,
    value=(
        "Por medio de la presente se hace constar que la joven Jennifer Vanesa "
        "Mac\u00edas Mu\u00f1oz est\u00e1 inscrita en esta instituci\u00f3n, donde recibe apoyo "
        "para seguir desarrollando sus habilidades conductuales, cognitivas, "
        "emocionales y sociales, desde el a\u00f1o 2018 a la fecha; observando "
        "siempre una puntual asistencia y constancia en su desempe\u00f1o."
    ),
)

col1, col2 = st.columns(2)
with col1:
    ciudad = st.text_input("Ciudad", value="Chihuahua, Chihuahua")
with col2:
    fecha = st.text_input("Fecha", value="los 19 d\u00edas del mes de Octubre del 2025")

st.divider()
st.subheader("Firma")

col_a, col_b = st.columns(2)
with col_a:
    nombre_firma = st.text_input("Nombre", value="Lic. Isabel Pazos")
    cargo_firma = st.text_input("Cargo", value="Directora")
with col_b:
    org_firma = st.text_input(
        "Organizaci\u00f3n",
        value="CONCERTINOS: Centro para personas con Diversidad Funcional",
    )

st.divider()
st.subheader("Datos de contacto")

col_x, col_y, col_z = st.columns(3)
with col_x:
    email = st.text_input("Email", value="isabellpazos@gmail.com")
with col_y:
    celular = st.text_input("Celular", value="614 1106956")
with col_z:
    direccion = st.text_input("Direcci\u00f3n", value="Calle Pino 607")

st.divider()

if st.button("Generar PDF", type="primary", use_container_width=True):
    pdf_buf = generate_pdf(
        titulo, cuerpo, ciudad, fecha,
        nombre_firma, cargo_firma, org_firma,
        email, celular, direccion,
    )
    st.download_button(
        label="Descargar PDF",
        data=pdf_buf,
        file_name="constancia.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.success("PDF generado correctamente.")
