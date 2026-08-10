# reporte_pdf.py
# MHD-INT PRO v5.2 — Capa 4: Reporte ejecutivo en PDF
# Licencia: Comercial propietaria (dual con AGPL-3.0)
#
# ⚠️ ESTE MÓDULO NO PERTENECE AL REPOSITORIO PÚBLICO AGPL.
# Genera un PDF ejecutivo de 1-2 páginas: resumen, desglose MHI, análisis y
# gráfica embebida. Soporta marca blanca (branding) opcional -- ver
# BRANDING_CLIENTE en app_streamlit_pro.py, desactivada por defecto (sin
# decisión de negocio tomada sobre en qué nivel va con el esquema de
# precios vigente: AGPL / Standard $49 / Pro $199). Fondo BLANCO (estilo
# publicación), a diferencia del dashboard oscuro.
#
# FIX v5.2 (revisión previa a release): la tabla "Desglose del MHI" solo
# mostraba los 4 componentes pesados, que no coinciden con mhi_total cuando
# hay penalización por oblicuidad -- un cliente pagando por este reporte
# vería una tabla que "no suma" sin ninguna explicación. Se agrega la fila
# de penalización (usa habitabilidad.calcular_mhi v5.1.1: mhi_bruto /
# penalizacion_obl_pts) para que la tabla reconcilie exactamente con el
# MHI total del resumen ejecutivo.

import os
import io
import tempfile
from datetime import datetime
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, HRFlowable)

from habitabilidad import categoria_mhi

VERSION_PRO = "5.2 Pro"
COLOR_ROJO = colors.HexColor('#E50914')
COLOR_AZUL = colors.HexColor('#0077B6')
COLOR_GRIS = colors.HexColor('#555555')
LOGO_DEFECTO = "assets/logo_mhd_int.png"


def _crear_figura_b_a(resultado):
    """Figura B_p + a vs tiempo (fondo blanco, estilo publicación)."""
    serie = resultado.serie
    t = np.array(serie.tiempos)
    b = np.array(serie.B_p_gauss)
    a = np.array(serie.a_ua)

    fig, ax1 = plt.subplots(figsize=(8, 4), dpi=150)
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    ax1.plot(t, b, color='#E50914', lw=2, label='B_p (Gauss)')
    ax1.set_xlabel('Tiempo (Gyr)', color='black')
    ax1.set_ylabel('B_p (Gauss)', color='#E50914')
    ax1.tick_params(axis='y', labelcolor='#E50914', colors='black')
    ax1.tick_params(axis='x', colors='black')

    ax2 = ax1.twinx()
    ax2.plot(t, a, color='#0077B6', lw=1.5, ls='--', label='a (UA)')
    ax2.set_ylabel('a (UA)', color='#0077B6')
    ax2.tick_params(axis='y', labelcolor='#0077B6')

    ax1.set_title(f'Evolución de {resultado.nombre_planeta}', color='black')
    ax1.grid(True, alpha=0.3)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='best', framealpha=0.9)
    return fig


def generar_reporte_pdf(resultado, mhi, params: dict, branding=None) -> bytes:
    """
    Genera un PDF ejecutivo. Devuelve los bytes del PDF.
    branding: dict opcional {"logo_path": str, "nombre_cliente": str} para
    marca blanca (nivel Código Fuente). None = marca "Solaris Core".
    """
    if not resultado.es_valido():
        raise ValueError(f"Resultado inválido: {resultado.error}")
    if not resultado.tiene_serie():
        raise ValueError("El resultado no tiene serie temporal; no se puede generar el PDF.")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        title=f"Reporte {resultado.nombre_planeta} — MHD-INT Pro",
        author=(branding or {}).get("nombre_cliente", "Solaris Core"),
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=20,
                                  textColor=COLOR_ROJO, spaceAfter=6)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13,
                              textColor=COLOR_ROJO, spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']

    nombre_marca = (branding or {}).get("nombre_cliente", "Solaris Core")
    story = []
    tmp_imgs = []

    # Encabezado
    logo_path = (branding or {}).get("logo_path", LOGO_DEFECTO)
    if os.path.exists(logo_path):
        try:
            story.append(Image(logo_path, width=1.2*inch, height=1.2*inch))
        except Exception:
            pass
    story.append(Paragraph("Reporte de Habitabilidad Planetaria", titulo_style))
    story.append(Paragraph(
        f"<b>{resultado.nombre_planeta}</b> · MHD-INT Pro v{VERSION_PRO} · "
        f"{datetime.now().strftime('%Y-%m-%d')}", normal_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ROJO, spaceAfter=10))

    # 1. Resumen ejecutivo
    story.append(Paragraph("1. Resumen ejecutivo", h2_style))
    estado = ("Estrellado" if resultado.se_estrello else
              "Sin atmósfera" if resultado.atm_perdida else "Estable")
    resumen_data = [
        ["Métrica", "Valor"],
        ["Estado final", estado],
        ["MHI total", f"{mhi['mhi_total']:.1f} / 100" if mhi else "N/D"],
        ["Categoría", categoria_mhi(mhi['mhi_total']) if mhi else "N/D"],
        ["Campo magnético final", f"{resultado.B_final_gauss:.4f} G"],
        ["Distancia orbital final", f"{resultado.a_final_ua:.4f} UA"],
        ["Excentricidad final", f"{resultado.e_final:.5f}"],
        ["Período de rotación final", f"{resultado.P_rot_final_dias:.3f} días"],
    ]
    t_res = Table(resumen_data, colWidths=[2.6*inch, 3.5*inch])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_ROJO),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    story.append(t_res)

    # 2. Desglose del MHI
    if mhi:
        story.append(Paragraph("2. Desglose del MHI", h2_style))
        mhi_data = [
            ["Componente", "Peso", "Valor", "Aporte (pts)"],
            ["Escudo magnético", "40%", f"{mhi['escudo_mag_pct']:.1f}% del tiempo",
             f"{mhi['escudo_mag_pct']*0.40:.1f}"],
            ["Campo activo", "30%", f"{mhi['campo_activo_pct']:.1f}% del tiempo",
             f"{mhi['campo_activo_pct']*0.30:.1f}"],
            ["Estabilidad orbital", "20%", f"e_prom = {mhi['e_promedio']:.4f}",
             f"{mhi['estabilidad_orb']*0.20:.1f}"],
            ["Calor de marea", "10%", f"Q_prom = {mhi['q_promedio_w']:.2e} W",
             f"{mhi['score_marea']*0.10:.1f}"],
        ]
        # FIX v5.2: fila de penalización por oblicuidad, solo si aplica.
        # Sin esta fila, las primeras 4 sumaban mhi_bruto, no mhi_total.
        penal = mhi.get("penalizacion_obl_pts", 0.0)
        if penal != 0.0:
            mhi_data.append([
                "Penalización oblicuidad", "—",
                f"ε final = {mhi['eps_final_deg']:.1f}° (fuera de 5°–60°)",
                f"{penal:+.1f}",
            ])
        mhi_data.append(["Subtotal / MHI total", "", "", f"{mhi['mhi_total']:.1f}"])

        t_mhi = Table(mhi_data, colWidths=[2.0*inch, 0.8*inch, 2.0*inch, 1.3*inch])
        estilo_mhi = [
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_AZUL),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8E8E8')),
        ]
        t_mhi.setStyle(TableStyle(estilo_mhi))
        story.append(t_mhi)
        if mhi['atm_perdida']:
            story.append(Spacer(1, 6))
            story.append(Paragraph(
                "<b>⚠ Atmósfera perdida:</b> el MHI fue forzado a 0. El escudo "
                "magnético no es útil sin atmósfera que proteger.", normal_style))
        if mhi['se_estrello']:
            story.append(Paragraph(
                "<b>💥 Planeta estrellado:</b> el MHI fue forzado a 0.", normal_style))

    # 3. Gráfica embebida
    story.append(Paragraph("3. Evolución temporal", h2_style))
    try:
        fig = _crear_figura_b_a(resultado)
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fig.savefig(tmp.name, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        tmp_imgs.append(tmp.name)
        story.append(Image(tmp.name, width=6.3*inch, height=3.15*inch))
    except Exception:
        story.append(Paragraph("No se pudo generar la gráfica.", normal_style))

    # Pie de análisis
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=6))
    story.append(Paragraph(
        f"Simulado con MHD-INT Pro v{VERSION_PRO}. t_max = {params.get('t_max_gyr', 5.0)} Gyr, "
        f"dt = {params.get('dt_yr', 10000)} años. Motor físico bajo AGPL-3.0; "
        f"este reporte se distribuye bajo licencia comercial a {nombre_marca}.",
        ParagraphStyle('Pie', parent=normal_style, fontSize=8, textColor=COLOR_GRIS)))

    def _footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(inch, 0.5*inch, f"MHD-INT Pro v{VERSION_PRO} · {nombre_marca}")
        canvas.drawRightString(letter[0]-inch, 0.5*inch, f"Página {doc_.page}")
        canvas.restoreState()

    try:
        doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    finally:
        for p in tmp_imgs:
            try:
                os.unlink(p)
            except Exception:
                pass

    return buffer.getvalue()
