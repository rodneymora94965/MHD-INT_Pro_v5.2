# pack_figuras.py
# MHD-INT PRO v5.2 — Capa 4: Pack de figuras en alta resolución (ZIP)
# Licencia: Comercial propietaria (dual con AGPL-3.0)
#
# ⚠️ ESTE MÓDULO NO PERTENECE AL REPOSITORIO PÚBLICO AGPL.
# Genera un ZIP en memoria con figuras PNG a 300 dpi (calidad publicación),
# una por variable física relevante. Fondo blanco (estilo publicación).

import io
import zipfile
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

VERSION_PRO = "5.2 Pro"
M_ATM_TIERRA_KG = 5.15e18


def _fig_simple(t, y, ylabel, titulo, color):
    """Figura limpia de una variable vs tiempo (fondo blanco)."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.plot(t, y, color=color, lw=2)
    ax.set_xlabel('Tiempo (Gyr)', color='black')
    ax.set_ylabel(ylabel, color='black')
    ax.set_title(titulo, color='black')
    ax.grid(True, alpha=0.3)
    ax.tick_params(colors='black')
    return fig


def generar_pack_figuras(resultado) -> bytes:
    """
    Genera un ZIP en memoria con las figuras del resultado. Devuelve bytes.
    Incluye solo las variables cuyo modelo realmente corrió.
    """
    if not resultado.tiene_serie():
        raise ValueError("El resultado no tiene serie temporal.")
    serie = resultado.serie
    t = np.array(serie.tiempos)
    nombre = resultado.nombre_planeta

    figuras = []

    figuras.append((f"{nombre}_campo_magnetico.png",
                    _fig_simple(t, np.array(serie.B_p_gauss), "B_p (Gauss)",
                                f"Campo magnético — {nombre}", "#E50914")))
    figuras.append((f"{nombre}_orbita.png",
                    _fig_simple(t, np.array(serie.a_ua), "a (UA)",
                                f"Distancia orbital — {nombre}", "#0077B6")))
    figuras.append((f"{nombre}_excentricidad.png",
                    _fig_simple(t, np.array(serie.e), "e",
                                f"Excentricidad — {nombre}", "#2A9D8F")))

    # Oblicuidad solo si es dato conocido
    if getattr(resultado, "eps_conocido", False) and serie.eps_deg:
        figuras.append((f"{nombre}_oblicuidad.png",
                        _fig_simple(t, np.array(serie.eps_deg), "ε (°)",
                                    f"Oblicuidad — {nombre}", "#FFA500")))

    # Atmósfera solo si el modelo corrió
    if serie.M_atm_kg and np.any(np.array(serie.M_atm_kg) > 0):
        M_atm_tierras = np.array(serie.M_atm_kg) / M_ATM_TIERRA_KG
        figuras.append((f"{nombre}_atmosfera.png",
                        _fig_simple(t, M_atm_tierras, "M_atm (Tierras)",
                                    f"Masa atmosférica — {nombre}", "#9B5DE5")))

    # Térmica solo si el modelo corrió
    if serie.T_cmb_K and np.any(np.array(serie.T_cmb_K) > 0):
        figuras.append((f"{nombre}_termica.png",
                        _fig_simple(t, np.array(serie.T_cmb_K), "T_cmb (K)",
                                    f"Temperatura CMB — {nombre}", "#F15BB5")))

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for nombre_archivo, fig in figuras:
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format='png', dpi=300, bbox_inches='tight',
                        facecolor='white')
            img_buf.seek(0)
            zf.writestr(nombre_archivo, img_buf.getvalue())
            plt.close(fig)

        metadata = (
            f"MHD-INT Pro v{VERSION_PRO} — Pack de figuras\n"
            f"Planeta: {nombre}\n"
            f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"\nFiguras incluidas:\n"
        )
        for nombre_archivo, _ in figuras:
            metadata += f"  - {nombre_archivo}\n"
        metadata += (
            "\nTodas las figuras: PNG, 300 dpi, fondo blanco (estilo publicación).\n"
            "Motor físico bajo AGPL-3.0; figuras generadas por la edición comercial.\n"
        )
        zf.writestr("LEEME.txt", metadata)

    return buffer.getvalue()
