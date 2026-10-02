# progreso_util.py
# MHD-INT — Sugerencia 4: logs en vivo (mensaje descriptivo, no solo %)
#
# Helper compartido para invocar un progress_callback de forma
# retrocompatible: si el callback es "viejo" (solo acepta la fracción),
# sigue funcionando igual que siempre. Si acepta también un mensaje
# opcional, se lo pasamos.
#
# CONVENCIÓN UNIFICADA: la fracción SIEMPRE es 0.0-1.0. Antes,
# engine.py.simular() pasaba 0-100 (porcentaje) y mapa_mhi.py pasaba
# 0-1 (fracción) -- dos convenciones distintas para la misma idea. Se
# normalizó a 0-1 en ambos lados porque, al revisar la UI, se confirmó
# que NADA dependía todavía del 0-100 de engine.py (no estaba
# conectado a ningún progress bar real) -- se pudo corregir sin
# riesgo de romper algo existente.


import inspect


def invocar_callback(callback, fraccion: float, mensaje: str = None) -> None:
    """
    Llama a 'callback' con (fraccion, mensaje) si lo acepta, o solo con
    (fraccion) si es un callback viejo de un solo argumento. 'fraccion'
    siempre 0.0-1.0.

    Usa inspect.signature() para decidir CUÁNTOS argumentos pasar antes
    de llamar (en vez de intentar con 2 y capturar TypeError como
    fallback) -- así un bug real dentro del callback no queda
    enmascarado como si fuera "el callback no acepta 2 argumentos".
    """
    if callback is None:
        return
    try:
        n_params = len(inspect.signature(callback).parameters)
    except (TypeError, ValueError):
        # No se pudo inspeccionar la firma (ej. builtin sin signature
        # disponible) -- se intenta con la forma nueva por defecto.
        n_params = 2
    if n_params >= 2:
        callback(fraccion, mensaje)
    else:
        callback(fraccion)
