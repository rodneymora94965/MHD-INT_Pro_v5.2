# guia_estudio.py
# MHD-INT — Guía de estudio (PDF), generada desde el contenido educativo real
# Licencia AGPL-3.0. Lógica pura, sin streamlit.
#
# NO es contenido nuevo: arma un PDF a partir de MARCO_TEORICO y las
# EJERCICIOS_* que ya existen en contenido_educativo.py, siguiendo la
# estructura de 5 módulos de la propuesta "Guía de estudio". Al tomar el
# contenido de ahí en vez de reescribirlo acá, hay una sola fuente de
# verdad -- si Educación cambia, esta guía cambia sola en la próxima
# generación, en vez de quedar una copia vieja dando vueltas.
import io
from datetime import datetime

from contenido_i18n import tm, traducir as T

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                HRFlowable, PageBreak)

COLOR_ROJO = colors.HexColor('#E50914')
COLOR_AZUL = colors.HexColor('#0077B6')
COLOR_GRIS = colors.HexColor('#555555')

# Selección curada de ejercicios de autoevaluación por módulo -- mismos
# títulos exactos que usa rutas_aprendizaje.py, para no mantener 2
# selecciones distintas del mismo contenido.
_EJERCICIOS_AUTOEVALUACION = {
    "Secundaria": ["El Futuro de la Tierra", "El Escudo Invisible (Campo Magnético)",
                  "La Pista de Baile (Excentricidad Orbital)"],
    "Universidad": ["Física del Campo Magnético (Número de Elsasser)",
                    "Resonancias en TRAPPIST-1", "Validación del Modelo con Datos Reales"],
    "Científico": ["Torque Atmosférico vs. Gravitatorio en Venus",
                   "Validación de Resonancias en Sistemas Reales",
                   "Calibración del Modelo de Dínamo", "El Problema del Paso Fijo en el Integrador"],
}


def _campos_ejercicio(nivel):
    if nivel == "Secundaria":
        return [(tm("guia.c.objetivo"), "objetivo"), (tm("guia.c.experimento"), "experimento"), (tm("guia.c.prediccion"), "prediccion")]
    if nivel == "Universidad":
        return [(tm("guia.c.concepto"), "concepto"), (tm("guia.c.practica"), "practica"), (tm("guia.c.simulacion"), "simulacion")]
    return [(tm("guia.c.pregunta"), "pregunta"), (tm("guia.c.metodo"), "metodo"), (tm("guia.c.analisis"), "analisis")]


def generar_guia_estudio_pdf(marco_teorico: dict, ejercicios_por_nivel: dict,
                             branding: dict = None) -> bytes:
    """
    Genera la Guía de Estudio completa (5 módulos) como PDF, tomando
    TODO su contenido de marco_teorico (MARCO_TEORICO real) y
    ejercicios_por_nivel ({"Secundaria": EJERCICIOS_SECUNDARIA, ...}).
    No inventa texto nuevo -- solo lo organiza y da formato.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            title=tm("guia.doc_title"),
                            author=(branding or {}).get("nombre_cliente", "Solaris Core"))

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=22,
                                  textColor=COLOR_ROJO, spaceAfter=6)
    modulo_style = ParagraphStyle('Modulo', parent=styles['Heading1'], fontSize=16,
                                  textColor=COLOR_ROJO, spaceBefore=18, spaceAfter=8)
    seccion_style = ParagraphStyle('Seccion', parent=styles['Heading2'], fontSize=12,
                                   textColor=COLOR_AZUL, spaceBefore=10, spaceAfter=4)
    subseccion_style = ParagraphStyle('Subseccion', parent=styles['Heading3'], fontSize=10,
                                      textColor=colors.HexColor('#333333'), spaceBefore=6, spaceAfter=2)
    normal_style = styles['Normal']
    nota_style = ParagraphStyle('Nota', parent=normal_style, fontSize=8, textColor=COLOR_GRIS)

    story = []

    # ---- Portada ----
    story.append(Paragraph(tm("guia.titulo"), titulo_style))
    story.append(Paragraph(tm("guia.subtitulo"), normal_style))
    story.append(Paragraph(f"Solaris Core · {datetime.now().strftime('%Y-%m-%d')}", nota_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ROJO, spaceAfter=10))
    story.append(Paragraph(
        tm("guia.intro"), normal_style))
    story.append(PageBreak())

    # ---- Módulo 1: Fundamentos de astrofísica planetaria ----
    story.append(Paragraph(tm("guia.m1"), modulo_style))
    for tema in marco_teorico["introduccion_astrofisica"]:
        story.append(Paragraph(T(tema["titulo"]), seccion_style))
        story.append(Paragraph(T(tema["texto"]), normal_style))
        story.append(Spacer(1, 4))

    # ---- Módulo 2: El motor MHD y sus componentes ----
    story.append(PageBreak())
    story.append(Paragraph(tm("guia.m2"), modulo_style))
    for pilar in marco_teorico["pilares"]:
        story.append(Paragraph(T(pilar["nombre"]), seccion_style))
        story.append(Paragraph(tm("guia.nivel_basico", x=T(pilar['basico'])), normal_style))
        story.append(Paragraph(tm("guia.nivel_avanzado", x=T(pilar['avanzado'])), normal_style))
        story.append(Spacer(1, 4))

    story.append(Paragraph(tm("guia.bucle"), seccion_style))
    _bucle = marco_teorico["bucle_motor"]
    story.append(Paragraph(T(_bucle["intro"]), normal_style))
    for paso in _bucle["pasos"]:
        story.append(Paragraph(T(paso), normal_style))
    story.append(Paragraph(T(_bucle["nota_torque_atmosferico"]), nota_style))

    # ---- Módulo 3: Dinámica orbital y N-cuerpos ----
    story.append(PageBreak())
    story.append(Paragraph(tm("guia.m3"), modulo_style))
    _temas_modulo3 = ["N-cuerpos", "Resonancias orbitales", "Alineaciones planetarias"]
    for tema in marco_teorico["temas_avanzados"]:
        if tema["nombre"] not in _temas_modulo3:
            continue
        story.append(Paragraph(T(tema["nombre"]), seccion_style))
        story.append(Paragraph(T(tema["explicacion"]), normal_style))
        story.append(Paragraph(tm("guia.en_mhdint", x=T(tema['relacion_mhd_int'])), nota_style))
        story.append(Spacer(1, 4))

    # ---- Módulo 4: Habitabilidad y MHI ----
    story.append(PageBreak())
    story.append(Paragraph(tm("guia.m4"), modulo_style))
    story.append(Paragraph(T(marco_teorico["mhi_intro"]), normal_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(tm("guia.comp_mhi"), seccion_style))
    for peso, nombre, desc in marco_teorico["formula_mhi"]:
        story.append(Paragraph(f"<b>{peso} — {T(nombre)}:</b> {T(desc)}", normal_style))
    story.append(Paragraph(T(marco_teorico["nota_penalizacion_oblicuidad"]), nota_style))
    story.append(Spacer(1, 8))
    _igm = marco_teorico["interpretacion_gravedad_magnetismo"]
    story.append(Paragraph(tm("guia.conexion"), seccion_style))
    story.append(Paragraph(T(_igm["intro"]), normal_style))
    story.append(Paragraph(tm("guia.ciclo", x=T(_igm['ciclo'])), normal_style))

    # ---- Módulo 5: Aplicaciones prácticas y casos de estudio ----
    story.append(PageBreak())
    story.append(Paragraph(tm("guia.m5"), modulo_style))
    for caso in _igm["casos"]:
        story.append(Paragraph(T(caso["nombre"]), seccion_style))
        story.append(Paragraph(T(caso["texto"]), normal_style))
        story.append(Spacer(1, 4))

    # ---- Ejercicios de autoevaluación ----
    story.append(PageBreak())
    story.append(Paragraph(tm("guia.ejercicios"), modulo_style))
    story.append(Paragraph(
        tm("guia.ej_nota"),
        nota_style))
    for nivel, titulos in _EJERCICIOS_AUTOEVALUACION.items():
        story.append(Paragraph(tm("guia.nivel", nivel=tm(f"guia.nivel.{nivel}")), seccion_style))
        ejercicios = ejercicios_por_nivel[nivel]
        campos = _campos_ejercicio(nivel)
        for titulo in titulos:
            ej = next((e for e in ejercicios if e["titulo"] == titulo), None)
            if ej is None:
                continue
            story.append(Paragraph(T(ej["titulo"]), subseccion_style))
            for etiqueta, campo in campos:
                valor = ej.get(campo)
                if valor and valor != "—":
                    story.append(Paragraph(f"<b>{etiqueta}:</b> {T(valor)}", normal_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
