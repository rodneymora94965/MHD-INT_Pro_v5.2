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
        return [("Objetivo", "objetivo"), ("Experimento", "experimento"), ("Predicción", "prediccion")]
    if nivel == "Universidad":
        return [("Concepto", "concepto"), ("Práctica", "practica"), ("Simulación", "simulacion")]
    return [("Pregunta", "pregunta"), ("Método", "metodo"), ("Análisis", "analisis")]


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
                            title="Guía de Estudio — MHD-INT",
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
    story.append(Paragraph("Guía de Estudio", titulo_style))
    story.append(Paragraph("MHD-INT — Simulador de Habitabilidad Magnética", normal_style))
    story.append(Paragraph(f"Solaris Core · {datetime.now().strftime('%Y-%m-%d')}", nota_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ROJO, spaceAfter=10))
    story.append(Paragraph(
        "Este documento organiza el contenido educativo real de MHD-INT en 5 "
        "módulos progresivos. Cada sección tiene su equivalente exacto dentro "
        "de la app, en 📚 Educación -- esta guía es un mapa de lectura, no un "
        "documento aparte.", normal_style))
    story.append(PageBreak())

    # ---- Módulo 1: Fundamentos de astrofísica planetaria ----
    story.append(Paragraph("Módulo 1 — Fundamentos de astrofísica planetaria", modulo_style))
    for tema in marco_teorico["introduccion_astrofisica"]:
        story.append(Paragraph(tema["titulo"], seccion_style))
        story.append(Paragraph(tema["texto"], normal_style))
        story.append(Spacer(1, 4))

    # ---- Módulo 2: El motor MHD y sus componentes ----
    story.append(PageBreak())
    story.append(Paragraph("Módulo 2 — El motor MHD y sus componentes", modulo_style))
    for pilar in marco_teorico["pilares"]:
        story.append(Paragraph(pilar["nombre"], seccion_style))
        story.append(Paragraph(f"<b>Nivel básico:</b> {pilar['basico']}", normal_style))
        story.append(Paragraph(f"<b>Nivel avanzado:</b> {pilar['avanzado']}", normal_style))
        story.append(Spacer(1, 4))

    story.append(Paragraph("El bucle del motor", seccion_style))
    _bucle = marco_teorico["bucle_motor"]
    story.append(Paragraph(_bucle["intro"], normal_style))
    for paso in _bucle["pasos"]:
        story.append(Paragraph(paso, normal_style))
    story.append(Paragraph(_bucle["nota_torque_atmosferico"], nota_style))

    # ---- Módulo 3: Dinámica orbital y N-cuerpos ----
    story.append(PageBreak())
    story.append(Paragraph("Módulo 3 — Dinámica orbital y N-cuerpos", modulo_style))
    _temas_modulo3 = ["N-cuerpos", "Resonancias orbitales", "Alineaciones planetarias"]
    for tema in marco_teorico["temas_avanzados"]:
        if tema["nombre"] not in _temas_modulo3:
            continue
        story.append(Paragraph(tema["nombre"], seccion_style))
        story.append(Paragraph(tema["explicacion"], normal_style))
        story.append(Paragraph(f"<i>En MHD-INT: {tema['relacion_mhd_int']}</i>", nota_style))
        story.append(Spacer(1, 4))

    # ---- Módulo 4: Habitabilidad y MHI ----
    story.append(PageBreak())
    story.append(Paragraph("Módulo 4 — Habitabilidad y MHI", modulo_style))
    story.append(Paragraph(marco_teorico["mhi_intro"], normal_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Componentes del MHI", seccion_style))
    for peso, nombre, desc in marco_teorico["formula_mhi"]:
        story.append(Paragraph(f"<b>{peso} — {nombre}:</b> {desc}", normal_style))
    story.append(Paragraph(marco_teorico["nota_penalizacion_oblicuidad"], nota_style))
    story.append(Spacer(1, 8))
    _igm = marco_teorico["interpretacion_gravedad_magnetismo"]
    story.append(Paragraph("Conexión gravedad-magnetismo", seccion_style))
    story.append(Paragraph(_igm["intro"], normal_style))
    story.append(Paragraph(f"<b>El ciclo:</b> {_igm['ciclo']}", normal_style))

    # ---- Módulo 5: Aplicaciones prácticas y casos de estudio ----
    story.append(PageBreak())
    story.append(Paragraph("Módulo 5 — Aplicaciones prácticas y casos de estudio", modulo_style))
    for caso in _igm["casos"]:
        story.append(Paragraph(caso["nombre"], seccion_style))
        story.append(Paragraph(caso["texto"], normal_style))
        story.append(Spacer(1, 4))

    # ---- Ejercicios de autoevaluación ----
    story.append(PageBreak())
    story.append(Paragraph("Ejercicios de autoevaluación", modulo_style))
    story.append(Paragraph(
        "Selección curada -- la misma secuencia que usa la 🗺️ Ruta de "
        "Aprendizaje dentro de la app, para practicar con guía paso a paso.",
        nota_style))
    for nivel, titulos in _EJERCICIOS_AUTOEVALUACION.items():
        story.append(Paragraph(f"Nivel {nivel}", seccion_style))
        ejercicios = ejercicios_por_nivel[nivel]
        campos = _campos_ejercicio(nivel)
        for titulo in titulos:
            ej = next((e for e in ejercicios if e["titulo"] == titulo), None)
            if ej is None:
                continue
            story.append(Paragraph(ej["titulo"], subseccion_style))
            for etiqueta, campo in campos:
                valor = ej.get(campo)
                if valor and valor != "—":
                    story.append(Paragraph(f"<b>{etiqueta}:</b> {valor}", normal_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
