import streamlit as st

from pdf_document import LOGO_PATH, LetterLayoutError, generate_pdf


st.set_page_config(page_title="Generador de Constancias - Concertinos", page_icon=":page_facing_up:")
st.image(LOGO_PATH, width=200)
st.title("Generador de Constancias")
st.markdown("Llena los campos, revisa la vista previa y descarga tu constancia en PDF.")

st.divider()

titulo = st.text_input("Título del documento", value="Constancia estudiantil")

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

st.subheader("Vista previa")
st.caption("Se actualiza al terminar de editar cada campo. El PDF descargado será igual a esta vista previa.")

try:
    document = generate_pdf(
        titulo, cuerpo, ciudad, fecha,
        nombre_firma, cargo_firma, org_firma,
        email, celular, direccion,
    )
except LetterLayoutError as error:
    st.warning(str(error))
else:
    if document.page_count > 1:
        st.info("La carta ocupa dos páginas para mantener el texto legible.")
    st.pdf(document.data, height="stretch", key="letter_preview")
    st.download_button(
        label="Descargar PDF",
        data=document.data,
        file_name="constancia.pdf",
        mime="application/pdf",
        type="primary",
        width="stretch",
        on_click="ignore",
    )
