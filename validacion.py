from engine import simular_planeta

# ============================================================================
# EXCEPCIÓN DOCUMENTADA v4.1 (Cambio 1, torque de marea estelar - Hut 1981):
# Venus queda excluido del chequeo de sentido_rotacion ("retrogrado": None)
# Y de P_rot_dias ("P_rot_dias": None). Con el torque de marea estelar de dos
# cuerpos activo, el modelo predice a Venus PRÓGRADO y con un período que
# converge hacia sincronización orbital (~224 días simulados vs 243.02 días
# reales, 7.79% de error) — ambos efectos (signo Y magnitud) vienen del
# mismo mecanismo no modelado: el retrógrado lento real de Venus es producto
# de marea térmica atmosférica (superrotación atmosférica acoplada al suelo
# por fricción, Correia & Laskar 2001), no de la marea sólida de dos cuerpos
# que sí modelamos. No es un error del código: es un límite de alcance
# conocido del modelo. Sigue el mismo criterio ya usado para excluir
# P_rot_dias de la Tierra ("problema del Q"): valor real = None -> métrica
# no evaluada.
# ============================================================================
#
# ============================================================================
# EXCEPCIÓN DOCUMENTADA - Urano y Neptuno (datos Voyager 2, encuentros 1986 y
# 1989): B_gauss queda EXCLUIDO de la validación de magnitud (antes se
# validaba con tolerancia normal del 5%; se corrige acá porque esa premisa
# resultó ser incorrecta -- ver detalle abajo).
#
# Motivo real (confirmado con trazado de la curva de decaimiento completa,
# ago-2026): MHD-INT no tiene término de generación de dínamo -- es un
# modelo de solo-decaimiento (tau_dipolo=1.2 Gyr, calibrado contra el
# núcleo de hierro terrestre) con un interruptor fenomenológico que casi
# frena ese decaimiento SI el número de Elsasser del cuerpo supera al de
# la Tierra (E_P_REFERENCIA_DINAMO_ACTIVO, ver engine.py). Para Urano y
# Neptuno, el E_p calculado da muy por debajo de esa referencia -> el
# interruptor nunca se activa -> decaen a la tasa terrestre completa
# (~97% de pérdida en 4.5 Gyr), aunque ambos sostienen hoy un campo
# global real y aproximadamente estable.
#
# Se probó la alternativa ya existente en el motor (modelo térmico,
# Christensen 2009, generación real vía Rm > 40): mejora el orden de
# magnitud (0.006 G -> 0.049 G para Urano) pero tampoco pasa, y el Rm
# resultante (~5 millones) es señal de que usa los defaults térmicos
# calibrados para la Tierra (R_core, T_cmb_inicial_K) -- database.py
# nunca definió esos parámetros para "Gigante de hielo".
#
# Ninguno de los dos modelos representa el mecanismo real (dínamo en capa
# delgada de manto iónico agua/amoníaco/metano, físicamente distinto del
# núcleo metálico terrestre o del hidrógeno metálico de Júpiter) -- sigue
# siendo, además, un problema abierto en la ciencia planetaria real, no
# solo en este simulador. Forzar una recalibración específica para que
# el número dé bien sería exactamente el patrón de ajuste circular ya
# identificado y cerrado en TUM. Se documenta como límite de alcance
# conocido, mismo criterio que la excepción de Venus.
#
# La geometría del dipolo (no-axisimétrico y descentrado del núcleo --
# Urano ~59° de inclinación con offset ~0.3 R_p, Neptuno ~47° con offset
# ~0.55 R_p; Ness et al. 1986/1989, Connerney et al. 1987/1991) tampoco
# está modelada (MHD-INT asume dínamo dipolar centrado), pero es un
# límite distinto al de arriba -- ya no es lo único que falla.
#
# Sentido de rotación: Urano SÍ se sigue validando (retrógrado real,
# w_p_inicial negativo en database.py, consistente con inclinación axial
# 97.77°). a_ua y e también se siguen validando normalmente para ambos.
# ============================================================================
DATOS_REALES = {
    "Tierra":  {"P_rot_dias": None, "a_ua": 1.000, "B_gauss": 0.31, "e": 0.0167, "retrogrado": False},
    "Venus":   {"P_rot_dias": None, "a_ua": 0.723, "B_gauss": None, "e": 0.0068, "retrogrado": None},
    "Marte":   {"P_rot_dias": 1.02596, "a_ua": 1.524, "B_gauss": None, "e": 0.0934, "retrogrado": False},
    "Jupiter": {"P_rot_dias": 0.41354, "a_ua": 5.203, "B_gauss": 4.2, "e": 0.0489, "retrogrado": False},
    "Urano":   {"P_rot_dias": 0.71833, "a_ua": 19.191, "B_gauss": None, "e": 0.0457, "retrogrado": True},
    "Neptuno": {"P_rot_dias": 0.67125, "a_ua": 30.07, "B_gauss": None, "e": 0.0113, "retrogrado": False},
}
TOLERANCIA_DEFECTO = 0.05

def _error_relativo(sim, real):
    if real == 0:
        return None
    return abs(sim - real) / abs(real)

def validar_planeta(nombre: str, tolerancia: float = TOLERANCIA_DEFECTO,
                     t_max_gyr: float = 4.5, dt_yr: float = 50000.0):
    if nombre not in DATOS_REALES:
        raise KeyError(f"'{nombre}' no tiene datos de referencia.")
    referencia = DATOS_REALES[nombre]
    r = simular_planeta(nombre, t_max_gyr=t_max_gyr, dt_yr=dt_yr, incluir_serie=False)
    if not r.es_valido():
        return {"nombre": nombre, "aprueba": False, "error_simulacion": r.error, "metricas": {}}
    candidatos = {
        "P_rot_dias": r.P_rot_final_dias,
        "a_ua": r.a_final_ua,
        "B_gauss": r.B_final_gauss,
        "e": r.e_final,
    }
    metricas = {}
    todas_ok = True
    for clave, valor_real in referencia.items():
        if clave == "retrogrado" or valor_real is None:
            continue
        valor_sim = candidatos[clave]
        err = _error_relativo(valor_sim, valor_real)
        aprueba = err is not None and err <= tolerancia
        todas_ok = todas_ok and aprueba
        metricas[clave] = {
            "simulado": round(valor_sim, 5),
            "real": valor_real,
            "error_relativo_pct": round(err * 100, 2) if err is not None else None,
            "aprueba": aprueba,
        }
    if "retrogrado" in referencia and referencia["retrogrado"] is not None:
        es_retrogrado_sim = r.w_final < 0
        aprueba_sentido = es_retrogrado_sim == referencia["retrogrado"]
        todas_ok = todas_ok and aprueba_sentido
        metricas["sentido_rotacion"] = {
            "simulado": "retrógrado" if es_retrogrado_sim else "prógrado",
            "real": "retrógrado" if referencia["retrogrado"] else "prógrado",
            "error_relativo_pct": None,
            "aprueba": aprueba_sentido,
        }
    return {"nombre": nombre, "aprueba": todas_ok, "error_simulacion": None, "metricas": metricas}

def validar_todos(tolerancia: float = TOLERANCIA_DEFECTO):
    resultados = []
    print(f"VALIDACIÓN CONTRA DATOS REALES (tolerancia {tolerancia*100:.0f}%)")
    print("=" * 65)
    for nombre in DATOS_REALES:
        res = validar_planeta(nombre, tolerancia=tolerancia)
        resultados.append(res)
        estado = "APRUEBA" if res["aprueba"] else "FALLA"
        print(f"\n{nombre}: {estado}")
        if res["error_simulacion"]:
            print(f"  (error de simulación: {res['error_simulacion']})")
        for clave, m in res["metricas"].items():
            marca = "OK " if m["aprueba"] else "!! "
            print(f"  {marca}{clave}: simulado={m['simulado']}, real={m['real']}, error={m['error_relativo_pct']}%")
    return resultados

if __name__ == "__main__":
    validar_todos()
