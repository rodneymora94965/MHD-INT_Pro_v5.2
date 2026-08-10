# video_mpl.py
# MHD-INT PRO v5.2 — Capa 1: Generador de video científico (Matplotlib + FFmpeg)
# Licencia: Comercial propietaria (dual con AGPL-3.0)
#
# ⚠️ ESTE MÓDULO NO PERTENECE AL REPOSITORIO PÚBLICO AGPL.
# Renderiza una animación MP4 (fallback: GIF) a partir del diccionario JSON
# que produce exportar_video.construir_json_video(). NO toca ninguna física.
#
# FIX v5.2 #1 — CRÍTICO (bloqueaba el 100% de las generaciones de video):
# `Animation.save()` de Matplotlib NO acepta un argumento `format=`, y en
# las versiones de Matplotlib probadas (3.10.x) tampoco acepta un objeto
# BytesIO como destino (aunque se le pase un `writer` explícito) -- exige
# una ruta de archivo real. El código original pasaba `format='mp4'`/
# `format='gif'` directamente a un buffer en memoria; eso siempre lanzaba
# TypeError, caía al bloque `except`, y terminaba agotando también el
# fallback a GIF por el mismo motivo -- es decir, la Capa 1 completa (la
# función insignia del producto Pro) fallaba siempre, en cualquier
# instalación, independientemente de si ffmpeg está presente. Se corrige
# renderizando a un archivo temporal real (mismo patrón que ya usa
# reporte_pdf.py para la figura embebida) y leyéndolo de vuelta a BytesIO
# para no cambiar el contrato con comparador.py / app_streamlit_pro.py.
#
# FIX v5.2 #2: el dict de exportar_video.py no incluía eps_deg por punto
# -> la línea de oblicuidad se graficaba plana en 0.0 en TODOS los videos,
# como si fuera un dato real. Se corrigió en exportar_video.py v5.1.1
# (agrega eps_deg + meta.eps_conocido). Este módulo ahora respeta esa
# bandera: si eps_conocido=False (la mayoría de los exoplanetas), la línea
# de oblicuidad NO se dibuja -- no se muestra como si fuera un dato
# conocido cuando no lo es. Ver CAMBIOS.md v5.1.1 y habitabilidad.py
# (mismo principio ya aplicado ahí desde v5.1).

import io
import os
import tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI — obligatorio en servidores Streamlit
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Tema oscuro corporativo MHD-INT (consistente con el CSS de app_streamlit_pro.py)
plt.style.use('dark_background')

# Paleta corporativa
COLOR_B   = '#E50914'    # Rojo       — campo magnético
COLOR_A   = '#00C9FF'    # Cian       — distancia orbital
COLOR_E   = '#92FE9D'    # Verde      — excentricidad
COLOR_EPS = '#FF6B6B'    # Rojo claro — oblicuidad
COLOR_ATM = '#FFA500'    # Naranja    — masa atmosférica
COLOR_BG  = '#0A0A0F'    # Fondo Streamlit
COLOR_LEG = '#1A1A2E'    # Fondo de leyendas

# Debajo de este número de puntos se usa GIF directo
MIN_PUNTOS_PARA_MP4 = 20

# FIX CRÍTICO: límite de frames del video. La serie puede tener hasta 2000
# puntos, pero renderizar 2000 frames tarda 30-120 s. Con 400 frames el
# render baja a ~5-10 s y la animación sigue siendo fluida.
MAX_FRAMES_VIDEO = 400


def _extraer_arrays_seguros(serie: list, eps_conocido: bool) -> dict:
    """Convierte la lista de dicts en arrays numpy, manejando campos ausentes.

    eps solo se extrae si eps_conocido=True; si no, se devuelve None para
    que el resto del pipeline sepa que no debe dibujarse (en vez de un
    array de ceros indistinguible de un dato real en 0°).
    """
    tiempos = np.array([p.get("t_Gyr", 0.0) for p in serie], dtype=float)
    a_ua    = np.array([p.get("a_ua", 0.0) for p in serie], dtype=float)
    b_gauss = np.array([p.get("B_p_Gauss", 0.0) for p in serie], dtype=float)
    e       = np.array([p.get("e", 0.0) for p in serie], dtype=float)
    atm     = np.array([p.get("M_atm_Tierras", 0.0) for p in serie], dtype=float)
    eps = None
    if eps_conocido:
        eps = np.array([p.get("eps_deg", 0.0) for p in serie], dtype=float)
    return dict(tiempos=tiempos, a_ua=a_ua, b_gauss=b_gauss, e=e, eps=eps, atm=atm)


def _limites_seguros(arr: np.ndarray, margen: float = 0.10) -> tuple:
    """Calcula (min, max) con margen, protegiéndose de arrays constantes o en cero."""
    if len(arr) == 0 or np.all(arr == 0):
        return 0.0, 1.0
    mn, mx = float(np.nanmin(arr)), float(np.nanmax(arr))
    if mn == mx:
        return mn * 0.9 if mn > 0 else -0.1, mx * 1.1 if mx > 0 else 0.1
    delta = (mx - mn) * margen
    return mn - delta, mx + delta


def generar_video_desde_dict(data: dict, fps: int = 20, dpi: int = 100) -> io.BytesIO:
    """
    Genera un video MP4 (o GIF como fallback) en memoria a partir del dict
    JSON producido por exportar_video.construir_json_video().
    Devuelve io.BytesIO; el atributo .formato_real indica 'mp4' o 'gif'.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Esperaba dict, recibió {type(data).__name__}")
    if "meta" not in data or "serie_temporal" not in data:
        raise ValueError("El dict debe tener claves 'meta' y 'serie_temporal'.")

    meta  = data["meta"]
    serie = data["serie_temporal"]
    if len(serie) < 2:
        raise ValueError(f"Serie demasiado corta ({len(serie)} puntos). Mínimo: 2.")

    eps_conocido = bool(meta.get("eps_conocido", False))
    arr = _extraer_arrays_seguros(serie, eps_conocido)
    tiempos = arr["tiempos"]
    a_ua    = arr["a_ua"]
    b_gauss = arr["b_gauss"]
    e       = arr["e"]
    eps     = arr["eps"]          # None si no es conocida
    atm     = arr["atm"]

    # Submuestreo de frames para el video (fix de rendimiento)
    if len(tiempos) > MAX_FRAMES_VIDEO:
        idx_video = np.linspace(0, len(tiempos) - 1, MAX_FRAMES_VIDEO).astype(int)
        tiempos = tiempos[idx_video]
        a_ua    = a_ua[idx_video]
        b_gauss = b_gauss[idx_video]
        e       = e[idx_video]
        if eps is not None:
            eps = eps[idx_video]
        atm     = atm[idx_video]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)
    fig.suptitle(
        f"Evolución de {meta.get('planeta', '?')} — MHD-INT",
        fontsize=14, color='white', weight='bold',
    )

    # Pre-calcular límites (evita jitter entre frames)
    t_max = float(tiempos[-1]) * 1.05
    b_min, b_max     = _limites_seguros(b_gauss)
    a_min, a_max     = _limites_seguros(a_ua, margen=0.05)
    e_max            = _limites_seguros(e)[1]
    eps_max          = _limites_seguros(eps)[1] if eps is not None else None
    atm_min, atm_max = _limites_seguros(atm)

    # Eje superior: Campo magnético + distancia orbital
    ax1.set_facecolor(COLOR_BG)
    ax1.set_title("Campo magnético y órbita", fontsize=11, color='white')
    ax1.set_xlim(0, t_max)
    ax1.set_ylim(b_min, b_max)
    ax1.set_xlabel("Tiempo (Gyr)", color='white')
    ax1.set_ylabel("B (Gauss)", color=COLOR_B)
    line_b, = ax1.plot([], [], lw=2, color=COLOR_B, label="B_p")
    ax1.tick_params(axis='y', labelcolor=COLOR_B, colors='white')
    ax1.tick_params(axis='x', colors='white')

    ax1b = ax1.twinx()
    ax1b.set_ylim(a_min, a_max)
    ax1b.set_ylabel("a (UA)", color=COLOR_A)
    line_a, = ax1b.plot([], [], lw=1.5, color=COLOR_A, linestyle="--", label="a")
    ax1b.tick_params(axis='y', labelcolor=COLOR_A)

    # Eje inferior: e, [ε si se conoce], atmósfera
    titulo_ax2 = "Excentricidad y atmósfera" if eps is None else "Excentricidad, oblicuidad y atmósfera"
    ax2.set_facecolor(COLOR_BG)
    ax2.set_title(titulo_ax2, fontsize=11, color='white')
    ax2.set_xlim(0, t_max)
    ax2.set_ylim(0, max(e_max, eps_max) if eps_max is not None else e_max)
    ax2.set_xlabel("Tiempo (Gyr)", color='white')
    ax2.set_ylabel("e" + (" / ε (°)" if eps is not None else ""), color=COLOR_E)
    line_e, = ax2.plot([], [], lw=2, color=COLOR_E, label="e")
    line_eps = None
    if eps is not None:
        line_eps, = ax2.plot([], [], lw=2, color=COLOR_EPS, linestyle="-.", label="ε (°)")
    ax2.tick_params(axis='y', labelcolor=COLOR_E, colors='white')
    ax2.tick_params(axis='x', colors='white')

    ax2b = ax2.twinx()
    ax2b.set_ylim(atm_min, atm_max)
    ax2b.set_ylabel("M_atm (Tierras)", color=COLOR_ATM)
    line_atm, = ax2b.plot([], [], lw=2, color=COLOR_ATM, linestyle=":", label="M_atm")
    ax2b.tick_params(axis='y', labelcolor=COLOR_ATM)

    # Nota visible cuando la oblicuidad no es un dato conocido, para que
    # nunca se lea el gráfico como "oblicuidad = dato ausente = 0°".
    if eps is None:
        ax2.text(
            0.985, 0.04, "ε no disponible para este cuerpo",
            transform=ax2.transAxes, ha='right', va='bottom',
            fontsize=8, color='#888888', style='italic',
        )

    def init():
        line_b.set_data([], [])
        line_a.set_data([], [])
        line_e.set_data([], [])
        if line_eps is not None:
            line_eps.set_data([], [])
        line_atm.set_data([], [])
        artists = [line_b, line_a, line_e, line_atm]
        if line_eps is not None:
            artists.append(line_eps)
        return artists

    def animate(i):
        t = tiempos[:i+1]
        line_b.set_data(  t, b_gauss[:i+1])
        line_a.set_data(  t, a_ua[:i+1])
        line_e.set_data(  t, e[:i+1])
        if line_eps is not None:
            line_eps.set_data(t, eps[:i+1])
        line_atm.set_data(t, atm[:i+1])
        artists = [line_b, line_a, line_e, line_atm]
        if line_eps is not None:
            artists.append(line_eps)
        return artists

    ax1.legend(loc="upper left", facecolor=COLOR_LEG, edgecolor='white',
               labelcolor='white', framealpha=0.85)
    ax2.legend(loc="upper left", facecolor=COLOR_LEG, edgecolor='white',
               labelcolor='white', framealpha=0.85)

    # blit=False es obligatorio con ejes twinx
    anim = FuncAnimation(
        fig, animate, init_func=init,
        frames=len(tiempos), interval=1000/fps,
        blit=False, repeat=False,
    )

    # FIX v5.2 #1: Matplotlib exige una ruta de archivo real para
    # Animation.save() (no acepta BytesIO ni format=). Se renderiza a un
    # archivo temporal y se lee de vuelta a BytesIO -- el resto del
    # producto (comparador.py, app_streamlit_pro.py) sigue recibiendo un
    # BytesIO con .formato_real, sin cambios en su contrato.
    buffer = io.BytesIO()
    formato_real = None

    if len(tiempos) >= MIN_PUNTOS_PARA_MP4:
        tmp_mp4 = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        tmp_mp4.close()
        try:
            anim.save(tmp_mp4.name, writer='ffmpeg', fps=fps, dpi=dpi, bitrate=2000)
            with open(tmp_mp4.name, 'rb') as f:
                buffer = io.BytesIO(f.read())
            formato_real = 'mp4'
        except Exception:
            buffer = io.BytesIO()
        finally:
            try:
                os.unlink(tmp_mp4.name)
            except OSError:
                pass

    if formato_real is None:
        tmp_gif = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
        tmp_gif.close()
        try:
            anim.save(tmp_gif.name, writer=PillowWriter(fps=fps))
            with open(tmp_gif.name, 'rb') as f:
                buffer = io.BytesIO(f.read())
            formato_real = 'gif'
        except Exception as exc:
            plt.close(fig)
            raise RuntimeError(f"No se pudo renderizar ni con ffmpeg ni con Pillow: {exc}") from exc
        finally:
            try:
                os.unlink(tmp_gif.name)
            except OSError:
                pass

    plt.close(fig)
    buffer.formato_real = formato_real  # type: ignore[attr-defined]
    return buffer
