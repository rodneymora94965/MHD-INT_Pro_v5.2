import numpy as np
from typing import Dict, Optional
import warnings

from models import ResultadoSimulacion, SerieTemporal
from stellar_evolution import EstrellaEvolutiva
from numba_functions import (
    calcular_presion_ram_numba,
    calcular_torque_magnetico_numba,
    calcular_calor_marea_numba,
    calcular_de_dt_numba,
    calcular_elsasser_numba,
    calcular_radio_magnetosferico_numba,
    corregir_radio_ohmico_numba,
    calcular_migracion_orbital_numba,
    calcular_torque_tide_estelar,  # NUEVO v4.1 (Cambio 1) - pendiente de agregar en numba_functions.py real
)

try:
    from database import PLANETAS, ESTRELLAS, LUNAS
except ImportError:
    PLANETAS = {}
    ESTRELLAS = {}
    LUNAS = {}
    warnings.warn("No se encontró database.py")

from termica import NucleoTermico     # NUEVO v4.2: modelo termico del nucleo
from atmosfera import Atmosfera       # NUEVO v5.0: modelo de escape atmosferico

MU_0 = 4.0 * np.pi * 1e-7
ALPHA = 0.05
G = 6.67430e-11
M_SOL = 1.98847e30
UA = 1.495978707e11
YR_SEC = 365.25 * 24 * 3600
R_TIERRA = 6.371e6

# ============================================================================
# CORRECCIÓN v4.1 (auditoría 2026-07-22, hallazgo #1):
# tau_dipolo estaba implícitamente en 1000 Gyr (TASA=0.001), pero el Marco
# Teórico §4.2 documenta ~1.2 Gyr para un núcleo terrestre. Se ajusta la tasa
# para que sea consistente: tau_dipolo[Gyr] = 1 / TASA_DECAIMIENTO_B_BASE.
# ============================================================================
TASA_DECAIMIENTO_B_BASE = 1.0 / 1.2  # -> tau_dipolo = 1.2 Gyr

# ============================================================================
# CORRECCIÓN v4.1 (hallazgo #10, recalibración acordada 2026-07-22):
# El umbral documentado E_p >= 1 (§4.1) es inalcanzable con B_p superficial
# (ver auditoría). Se recalibra contra una referencia física real: el E_p
# inicial de la Tierra, el más débil de los dos cuerpos del dataset con
# dínamo activo confirmado hoy (Tierra y Júpiter). Venus y Marte (sin campo
# global hoy) quedan 4-8 órdenes de magnitud por debajo de esta referencia,
# lo cual separa naturalmente "activo" de "inactivo" sin ajustar a mano
# para que un resultado final coincida con un valor observado (evitar el
# patrón de ajuste circular ya identificado y cerrado en TUM).
#
# IMPORTANTE: esto sigue sin ser un modelo de generación de dínamo. Es un
# interruptor (ahora continuo en vez de binario) sobre la MISMA ecuación de
# solo-decaimiento. No hay término que haga crecer B_p; no hay retroalimen-
# tación con convección del núcleo ni con la rotación real. Es una
# aproximación fenomenológica, documentada como tal.
# ============================================================================
E_P_REFERENCIA_DINAMO_ACTIVO = 8.739480e-4  # E_p inicial de la Tierra (calibración empírica)


def estimar_B_estrella(tipo_espectral: str) -> float:
    tipo = tipo_espectral.strip().upper()
    if tipo.startswith('O') or tipo.startswith('B'):
        return 5.0e-2
    elif tipo.startswith('A') or tipo.startswith('F'):
        return 5.0e-3
    elif tipo.startswith('G'):
        return 1.0e-4
    elif tipo.startswith('K'):
        return 2.0e-4
    elif tipo.startswith('M'):
        return 5.0e-3
    else:
        return 1.0e-4


def estimar_L_estrella(masa_estrella_kg: float) -> float:
    """Estima la luminosidad estelar en luminosidades solares (L/L_sol) a
    partir de la masa real de la estrella, usando la relación
    masa-luminosidad de secuencia principal (Eker et al. 2018; Salaris &
    Cassisi 2005 para la rama de enanas M de baja masa):

        L/L_sol = (M/M_sol)^3.5           si M >= 0.43 M_sol
        L/L_sol = 0.23 * (M/M_sol)^2.3    si M <  0.43 M_sol

    Se usa masa en vez de una tabla por texto de tipo espectral (ej.
    "M3.5V") porque la base de datos tiene 25 subtipos espectrales
    distintos en 38 estrellas -- una tabla por string exacto quedaría
    incompleta con cualquier estrella nueva que se agregue, mientras que
    la masa ya es un dato numerico preciso disponible para todas.

    NOTA: reemplaza el valor fijo L_estrella=1.0 (luminosidad solar) que
    usaba el modelo termico para todas las estrellas por igual -- ver
    Marco_Teorico_v5_0.md §4.5, limitacion documentada. Con esta funcion,
    una enana M tipica (0.15 M_sol) da L ~= 0.003 L_sol en vez de 1.0 L_sol,
    lo que baja su T_superficie estimada y por lo tanto Q_CMB.
    """
    razon_masa = masa_estrella_kg / M_SOL
    if razon_masa >= 0.43:
        return razon_masa ** 3.5
    return 0.23 * (razon_masa ** 2.3)


class _EstadoInterno:
    __slots__ = ["t", "a", "w_p", "B_p", "P_ram", "E_p", "R_m_norm", "tau_mag",
                 "tiempo_migracion", "e", "Q_tidal", "a_luna",
                 "T_cmb", "B_gen", "Rm", "q_conv", "M_atm", "atm_perdida", "eps"]

    def __init__(self, t, a, w_p, B_p, P_ram, E_p, R_m_norm, tau_mag, tiempo_migracion,
                 e=0.0, Q_tidal=0.0, a_luna=0.0,
                 T_cmb=0.0, B_gen=0.0, Rm=0.0, q_conv=0.0, M_atm=0.0, atm_perdida=False,
                 eps=0.0):
        self.t, self.a, self.w_p, self.B_p = t, a, w_p, B_p
        self.P_ram, self.E_p, self.R_m_norm = P_ram, E_p, R_m_norm
        self.tau_mag, self.tiempo_migracion = tau_mag, tiempo_migracion
        self.e, self.Q_tidal = e, Q_tidal
        self.a_luna = a_luna
        self.T_cmb, self.B_gen, self.Rm, self.q_conv = T_cmb, B_gen, Rm, q_conv
        self.M_atm, self.atm_perdida = M_atm, atm_perdida
        self.eps = eps


class MotorMHD:
    def __init__(self, nombre_planeta: str,
                 parametros_extra: Optional[Dict] = None,
                 estrellas: Optional[Dict] = None,
                 planetas_db: Optional[Dict] = None,
                 lunas: Optional[Dict] = None,
                 estrella_personalizada: Optional[Dict] = None,
                 lunas_personalizadas: Optional[Dict] = None):

        # FIX v5.9 (revision previa a "Modo Sintetico avanzado"): si no se
        # pasa un dict explicito, planetas_db/estrellas_db/lunas_db quedaban
        # siendo EL MISMO objeto que PLANETAS/ESTRELLAS/LUNAS de database.py
        # (modulo compartido por todo el proceso). Cualquier mutacion de
        # abajo (estrella_personalizada, lunas_personalizadas) escribia
        # directo sobre la base de datos global -- confirmado con prueba:
        # una sola corrida sintetica con estrella_personalizada dejaba
        # PLANETAS["Tierra"]["estrella"] = "Estrella_Personalizada" de forma
        # PERMANENTE para el resto del proceso, afectando a cualquier
        # simulacion posterior de la Tierra real (Validacion, Comparador, u
        # otro usuario en el mismo servidor Streamlit). copy() a nivel
        # superior aisla esa mutacion a esta instancia de MotorMHD.
        self.planetas_db = dict(planetas_db or PLANETAS or {})
        self.estrellas_db = dict(estrellas or ESTRELLAS or {})
        self.lunas_db = dict(lunas or LUNAS or {})

        if estrella_personalizada:
            nombre_estrella_override = "Estrella_Personalizada"
            if nombre_estrella_override not in self.estrellas_db:
                self.estrellas_db[nombre_estrella_override] = {
                    "masa": estrella_personalizada["masa_kg"],
                    "tipo_espectral": estrella_personalizada["tipo_espectral"],
                    "edad_gyr": estrella_personalizada.get("edad_gyr", 4.6)
                }
            # FIX v5.9: un dict() de nivel superior sigue apuntando a los
            # MISMOS sub-diccionarios internos (copia superficial). Si
            # nombre_planeta ya existia en PLANETAS (caso normal: modo
            # Sintetico parte de "Tierra"), escribir directo en
            # self.planetas_db[nombre_planeta]["estrella"] seguia mutando
            # el dict real de la Tierra. Se copia la entrada del planeta
            # ANTES de tocarla.
            entrada_planeta = dict(self.planetas_db.get(nombre_planeta, {}))
            entrada_planeta["estrella"] = nombre_estrella_override
            self.planetas_db[nombre_planeta] = entrada_planeta

        if lunas_personalizadas:
            # FIX v5.9: mismo patron que arriba -- ahora self.lunas_db ya es
            # una copia de nivel superior, asi que .update() solo pisa la
            # clave dentro de esta copia (p.ej. "Tierra" para modo
            # Sintetico), sin tocar LUNAS["Tierra"] global.
            self.lunas_db.update(lunas_personalizadas)

        if nombre_planeta not in self.planetas_db:
            raise ValueError(f"Planeta '{nombre_planeta}' no encontrado.")

        self.nombre_planeta = nombre_planeta
        self.parametros = self.planetas_db[nombre_planeta].copy()
        if parametros_extra:
            self.parametros.update(parametros_extra)

        self._cargar_estrella()

        self.M = self.parametros["M"]
        self.R_p = self.parametros["R_p"]
        self.inercia = self.parametros["inercia"]
        self.rho_core = self.parametros["densidad_nucleo"]
        self.eta = self.parametros["difusividad"]
        self.rho_sw_base = self.parametros["rho_sw"]
        self.v_sw_base = self.parametros["v_sw"]
        self.w_estrella = self.parametros["w_estrella"]
        self.I = self.inercia * self.M * (self.R_p ** 2)

        # ================================================================
        # NUEVO v4.2 + v5.0: Modelo Termico del Nucleo + Atmosfera
        # (fusionado y corregido -- ver notas en termica.py / atmosfera.py)
        # ================================================================
        R_core = self.parametros.get("R_core", 0.55 * self.R_p)
        T_cmb = self.parametros.get("T_cmb_inicial_K", 4000.0)
        T_manto = self.parametros.get("T_manto_inicial_K", 2000.0)
        cp = self.parametros.get("cp_core", 840.0)
        H_radio = self.parametros.get("H_radiogenic", 1.5e-12)
        k_core = self.parametros.get("k_core", 40.0)
        tau_regen = self.parametros.get("tau_regen_yr", 1e8)
        # k_manto, regimen_tectonico y albedo se leen desde self.parametros
        # (definidos por planeta en database.py) en vez de usar valores
        # fijos internos, para que cada planeta use su dato real.
        k_manto = self.parametros.get("k_manto", 3.0)
        regimen_tectonico = self.parametros.get("regimen_tectonico", 1)
        albedo = self.parametros.get("albedo", 0.3)

        self.usar_modelo_termico = self.parametros.get("modelo_termico", False)
        if self.usar_modelo_termico:
            # C_calib=1.4215e-8: constante de calibracion de la ley de escala
            # de Christensen para el campo generado en el nucleo, ajustada
            # para que la Tierra (con el acoplamiento nucleo-manto activo)
            # reproduzca el campo superficial real de ~0.31 G.
            self.nucleo = NucleoTermico(
                M_planeta=self.M,
                R_planeta=self.R_p,
                R_core=R_core,
                rho_core=self.rho_core,
                T_cmb_inicial=T_cmb,
                T_manto_inicial=T_manto,
                cp_core=cp,
                H_radiogenic=H_radio,
                k_core=k_core,
                tau_regen_yr=tau_regen,
                C_calib=1.4215e-8,  # calibrado para B_superficial(Tierra) = 0.31 G
                k_manto=k_manto,
                regimen_tectonico=regimen_tectonico,
                albedo=albedo,
            )
        else:
            self.nucleo = None

        M_atm_ini = self.parametros.get("M_atm_inicial", 1e-6 * self.M)
        F_XUV = self.parametros.get("F_XUV_inicial", 1.0)
        eta_esc = self.parametros.get("eficiencia_escape", 0.15)
        tipo_estrella_atm = self.parametros.get("_tipo_espectral_estrella", "G2V")
        a_ua_inicial = self.parametros.get("a_inicial", 1.0 * UA) / UA

        self.usar_atmosfera = self.parametros.get("modelo_atmosfera", False)
        if self.usar_atmosfera:
            self.atmosfera = Atmosfera(
                M_atm_inicial=M_atm_ini,
                M_planeta=self.M,
                R_planeta=self.R_p,
                F_XUV_inicial=F_XUV,
                distancia_ua=a_ua_inicial,
                eficiencia_escape=eta_esc,
                tipo_estrella=tipo_estrella_atm,
            )
            self.M_atm_inicial_registro = M_atm_ini
        else:
            self.atmosfera = None
            self.M_atm_inicial_registro = 0.0
        # ================================================================
        self.e_inicial = self.parametros.get("e_inicial", 0.0)
        # NUEVO v5.1 (oblicuidad): eps_conocido distingue "no tenemos el dato"
        # de "sabemos que es 0". Ver fix A.5 en el informe de revision --
        # habitabilidad.py NO penaliza cuando eps_conocido=False.
        self.eps_inicial = np.radians(self.parametros.get("eps_inicial_deg", 0.0))
        self.eps_conocido = self.parametros.get("eps_conocido", False)

        self.luna = self.lunas_db.get(nombre_planeta)
        self.a_luna_inicial = self.luna["a_luna_inicial"] if self.luna else 0.0

        if self.nombre_planeta == "Mercurio":
            self.k2_sobre_q = 0.0
        elif self.R_p > 3.0 * R_TIERRA:
            self.k2_sobre_q = 1.0e-5
        else:
            self.k2_sobre_q = 0.015
        if parametros_extra and "k2_sobre_q" in parametros_extra:
            self.k2_sobre_q = parametros_extra["k2_sobre_q"]

        # --------------------------------------------------------------
        # MEJORA v4.1 (experimentos controlados): flags para aislar el
        # efecto de cada torque sobre la rotación. Default True en los 3
        # -> comportamiento idéntico al de siempre si no se especifican.
        # Pensado para depuración ("¿cuál torque causa este comportamiento
        # raro?") y para fines didácticos en la interfaz sintética.
        # --------------------------------------------------------------
        self.torque_magnetico_on = self.parametros.get("torque_magnetico", True)
        self.torque_marea_estelar_on = self.parametros.get("torque_marea_estelar", True)
        self.torque_lunar_on = self.parametros.get("torque_lunar", True)

        self.MU_0 = MU_0
        self.G = G
        self.ALPHA = ALPHA

        nombre_estrella = self.parametros.get("estrella", "Sol")
        self.estrella_evolutiva = EstrellaEvolutiva(
            nombre_estrella,
            self.M_estrella,
            self.parametros.get("_tipo_espectral_estrella", "G2V"),
            B_inicial_tesla=self.B_estrella,  # <-- CORRECCIÓN v4.1: fuente única (ver adenda A.4)
        )
        self.estrella_evolutiva.set_viento_base(self.rho_sw_base, self.v_sw_base)
        # --------------------------------------------------------------
        # CORRECCIÓN v4.1 (hallazgo #3): EstrellaEvolutiva traía un
        # omega_actual fijo en 2.9e-6 para TODAS las estrellas, ignorando
        # el w_estrella específico de cada sistema en database.py. Se
        # alinea el estado inicial de la clase con el valor real del
        # sistema para que la evolución temporal parta del punto correcto.
        # --------------------------------------------------------------
        self.estrella_evolutiva.omega_actual = self.w_estrella

    def _cargar_estrella(self):
        nombre_estrella = self.parametros.get("estrella")
        if nombre_estrella and nombre_estrella in self.estrellas_db:
            estrella = self.estrellas_db[nombre_estrella]
            tipo = estrella.get("tipo_espectral", "G2V")
            self.parametros["B_estrella"] = estimar_B_estrella(tipo)
            self.parametros["M_estrella"] = estrella.get("masa", M_SOL)
            self.parametros["_tipo_espectral_estrella"] = tipo
        else:
            warnings.warn(f"Estrella '{nombre_estrella}' no encontrada; usando Sol.")
            self.parametros["B_estrella"] = 1.0e-4
            self.parametros["M_estrella"] = M_SOL
            self.parametros["_tipo_espectral_estrella"] = "G2V"

        self.B_estrella = self.parametros["B_estrella"]
        self.M_estrella = self.parametros["M_estrella"]
        # NUEVO v5.3: luminosidad real por masa (ver estimar_L_estrella),
        # en vez del valor fijo L_estrella=1.0 que usaba el modelo termico
        # para cualquier estrella. Afecta unicamente al balance termico del
        # nucleo (§4.5) cuando modelo_termico=True; el resto del motor no
        # la usa.
        self.L_estrella = estimar_L_estrella(self.M_estrella)

    def calcular_tiempo_migracion(self, a: float, Q: float = 100.0) -> float:
        n = np.sqrt(G * self.M_estrella / a**3)
        tipo = self.parametros.get("tipo_planeta", "")
        es_enana_M = self.parametros.get("_tipo_espectral_estrella", "").upper().startswith("M")
        if tipo in ["Gigante gaseoso", "Hot Jupiter", "SubNeptuno"]:
            Q_efectivo = 1e5
        elif es_enana_M:
            Q_efectivo = 1e6
        else:
            Q_efectivo = Q
        tau_mig = (2.0 / 63.0) * Q_efectivo * (self.M / self.M_estrella) * (a / self.R_p)**5 * (1.0 / n)
        return float(np.clip(tau_mig, 1e3 * YR_SEC, 1e20 * YR_SEC))

    def calcular_torque_lunar(self, a_luna: float, w_p: float) -> float:
        if self.luna is None or a_luna <= 0:
            return 0.0
        M_luna = self.luna["masa"]
        k2 = self.luna["k2"]
        Q_p = self.luna["Q_p"]
        n_luna = np.sqrt(G * self.M / a_luna ** 3)
        tau_magnitud = 1.5 * (k2 / Q_p) * G * (M_luna ** 2) * (self.R_p ** 5) / (a_luna ** 6)
        delta = w_p - n_luna
        if delta > 0:
            return -tau_magnitud
        elif delta < 0:
            return tau_magnitud
        else:
            return 0.0

    def calcular_recesion_lunar(self, a_luna: float, tau_lunar: float) -> float:
        if self.luna is None or a_luna <= 0:
            return 0.0
        M_luna = self.luna["masa"]
        factor = 0.5 * M_luna * np.sqrt(G * self.M / a_luna)
        if factor == 0:
            return 0.0
        return -tau_lunar / factor

    def _paso_temporal(self, estado: _EstadoInterno, dt: float) -> _EstadoInterno:
        t = estado.t + dt
        a, w_p, B_p, e = estado.a, estado.w_p, estado.B_p, estado.e

        # --------------------------------------------------------------
        # CORRECCIÓN v4.1 (hallazgo #3): se evoluciona la estrella en el
        # tiempo (Ley de Skumanich, viento estelar dependiente de omega)
        # en vez de usar rho_sw_base / v_sw_base / w_estrella fijos.
        # NOTA: no se pasa a_ua a evolucionar() porque la dependencia con
        # la distancia (a/UA)^-2 ya la aplica calcular_presion_ram_numba
        # por separado (Marco Teórico §3.1); pasarla aquí también
        # duplicaría el escalamiento por distancia.
        # --------------------------------------------------------------
        t_gyr = t / (1e9 * YR_SEC)
        # NOTA (adenda A.4): B_estrella_t se calcula pero, igual que antes de
        # la consolidación, todavía no alimenta P_ram ni tau_mag — la física
        # actual del modelo no correlaciona el campo estelar con la presión
        # de viento. Queda disponible (ya no descartado) por si se decide
        # wireearlo en una futura versión del modelo.
        w_estrella_t, B_estrella_t, rho_sw_t, v_sw_t = self.estrella_evolutiva.evolucionar(t_gyr)

        P_ram = calcular_presion_ram_numba(a, rho_sw_t, v_sw_t, UA)
        tau_mag = calcular_torque_magnetico_numba(a, w_p, B_p, P_ram, self.R_p, w_estrella_t, MU_0)
        E_p = calcular_elsasser_numba(B_p, w_p, self.rho_core, self.eta, MU_0)
        R_m_puro = calcular_radio_magnetosferico_numba(B_p, P_ram, MU_0)
        R_m_corr = corregir_radio_ohmico_numba(R_m_puro, E_p, ALPHA)

        # --------------------------------------------------------------
        # CORRECCIÓN v4.1 (hallazgo #2): se calcula R_ohm explícitamente
        # y se aplica a tau_mag en la ecuación de rotación, tal como
        # especifica el Marco Teórico §6: domega_p/dt = (tau_mag·R_ohm + tau_lunar)/I_p
        # Antes, R_ohm solo afectaba al radio reportado (R_m_norm), no a
        # la dinámica real de rotación.
        # --------------------------------------------------------------
        R_ohm = 1.0 + ALPHA * np.tanh(E_p - 1.0)

        # ============================================================
        # NUEVO v5.1: calor de marea total = excentricidad + oblicuidad.
        # Q_tidal_e es el termino original (v4.1); Q_tidal_obl se suma solo
        # si el planeta tiene oblicuidad apreciable (estado.eps > 0.01 rad).
        # Usa estado.eps (valor del paso anterior), consistente con el resto
        # de la funcion que usa estado.* para las cantidades "viejas".
        # ============================================================
        Q_tidal_e = calcular_calor_marea_numba(a, e, self.R_p, self.M_estrella, self.k2_sobre_q, G)
        if estado.eps > 0.01:
            factor_obl = (np.sin(estado.eps) ** 2) / max((1.0 - e ** 2) ** 1.5, 1e-12)
            Q_tidal_obl = 0.5 * Q_tidal_e * factor_obl
        else:
            Q_tidal_obl = 0.0
        Q_tidal_total = Q_tidal_e + Q_tidal_obl
        # ============================================================
        de_dt = calcular_de_dt_numba(a, e, self.R_p, self.M, self.M_estrella, self.k2_sobre_q, G)

        tiempo_migracion = self.calcular_tiempo_migracion(a)
        da_dt = calcular_migracion_orbital_numba(a, tiempo_migracion, YR_SEC)

        a_luna = estado.a_luna
        tau_lunar = self.calcular_torque_lunar(a_luna, w_p)
        # NOTA (Mejora 4): da_luna_dt (recesión orbital de la Luna) se
        # calcula siempre, independiente del toggle torque_lunar_on. El
        # toggle aísla el efecto del torque lunar sobre la ROTACIÓN del
        # planeta (para depuración/didáctica); la evolución orbital de la
        # Luna en sí es un proceso físico separado que no tiene sentido
        # apagar a medias.
        da_luna_dt = self.calcular_recesion_lunar(a_luna, tau_lunar)

        # --------------------------------------------------------------
        # CORRECCIÓN v4.1 (Cambio 1): torque de marea sólida de la estrella
        # sobre la rotación del planeta (Hut 1981). Domina sobre el torque
        # magnético para a < 0.1 UA (Hot Jupiters); antes no existía y la
        # rotación de esos planetas no evolucionaba por marea estelar.
        # Siempre activo, sin flag; signo depende de si w_p es mayor o
        # menor que el movimiento medio orbital n. Antes activo siempre sin
        # flag; ahora respeta self.torque_marea_estelar_on (ver Mejora 4,
        # experimentos controlados, más abajo).
        #
        # EXCEPCIÓN DOCUMENTADA - VENUS: con este torque activo, el modelo
        # predice a Venus PRÓGRADO (correcto para marea de dos cuerpos).
        # El retrógrado real de Venus es producto de marea térmica
        # atmosférica (Correia & Laskar 2001), mecanismo no modelado aquí.
        # Venus queda excluido del chequeo de sentido de rotación en
        # validacion.py por este motivo (ver comentario ahí).
        # --------------------------------------------------------------
        n = np.sqrt(G * self.M_estrella / (a ** 3))

        # ============================================================
        # Evolucion secular de la oblicuidad (Laskar & Robutel 1993,
        # version simplificada). Requiere "n" ya calculado arriba.
        # ============================================================
        if self.k2_sobre_q > 0:
            factor_amort = 1.5 * self.k2_sobre_q * (self.M_estrella / self.M) * ((self.R_p / a) ** 5)
            deps_dt = -factor_amort * n * np.sin(2.0 * estado.eps) * (1.0 + 0.5 * (e ** 2))
        else:
            deps_dt = 0.0
        eps_nuevo = max(0.0, estado.eps + deps_dt * dt)
        # ============================================================

        tau_tide_star = calcular_torque_tide_estelar(
            self.k2_sobre_q, self.M_estrella, self.R_p, a, w_p, n
        )

        # --------------------------------------------------------------
        # MEJORA v4.1 (experimentos controlados): cada torque se suma solo
        # si su flag está activa. Con las 3 en True (default) el resultado
        # es idéntico a antes de esta mejora.
        # --------------------------------------------------------------
        tau_total = 0.0
        if self.torque_magnetico_on:
            tau_total += tau_mag * R_ohm
        if self.torque_marea_estelar_on:
            tau_total += tau_tide_star
        if self.torque_lunar_on:
            tau_total += tau_lunar

        dw_p_dt = tau_total / self.I
        w_p_nuevo = w_p + dw_p_dt * dt
        if abs(w_p_nuevo) < 1e-20:
            w_p_nuevo = 1e-20 if w_p_nuevo >= 0 else -1e-20

        a_nuevo = max(a + da_dt * dt, 0.001 * UA)
        a_luna_nuevo = max(a_luna + da_luna_dt * dt, self.R_p) if self.luna else 0.0

        # --------------------------------------------------------------
        # CORRECCIÓN v4.1 (hallazgo post-validación, opción 3 acordada):
        # Sin regeneración por dínamo, tau_dipolo=1.2 Gyr hacía que CUALQUIER
        # planeta perdiera ~97.65% de su campo en 4.5 Gyr, incluida la Tierra
        # (que sí sostiene su dínamo activo). Se modula la tasa de decaimiento
        # según el número de Elsasser: si el dínamo está activo (E_p >= 1),
        # el decaimiento casi se anula; si está apagado (E_p < 1), decae con
        # tau_dipolo=1.2 Gyr real. No es un modelo de generación completo
        # (eso sería un término de regeneración explícito, ver auditoría),
        # pero evita el colapso artificial de campos con dínamo activo.
        # --------------------------------------------------------------
        factor_dinamo = float(np.clip(E_p / E_P_REFERENCIA_DINAMO_ACTIVO, 0.0, 1.0))
        tasa_efectiva = TASA_DECAIMIENTO_B_BASE * (1.0 - factor_dinamo * 0.99)

        # ============================================================
        # NUEVO v4.2 + v5.0: GENERACION DE CAMPO CON MODELO TERMICO Y
        # ACTUALIZACION DE ATMOSFERA (fusionado, ver notas en termica.py /
        # atmosfera.py). Si el toggle esta apagado, el comportamiento es
        # identico al de v4.1 (interruptor fenomenologico).
        # ============================================================
        if self.usar_modelo_termico and self.nucleo is not None:
            q_conv, T_cmb_nuevo = self.nucleo.actualizar(dt, a / UA, L_estrella=self.L_estrella)
            B_gen_core = self.nucleo.calcular_B_gen(q_conv)
            B_gen_sup = self.nucleo.atenuar_a_superficie(B_gen_core, self.R_p)
            Rm = self.nucleo.calcular_Rm(q_conv, self.eta)
            dinamo_activo = Rm > 40.0

            if dinamo_activo:
                tau_efectivo = self.nucleo.tau_regen
                dB_dt = -(B_p - B_gen_sup) / tau_efectivo
            else:
                tau_dipolo = 1.2 * 1e9 * YR_SEC
                dB_dt = -B_p / tau_dipolo
            B_p_nuevo = max(B_p + dB_dt * dt, 1e-8)
        else:
            B_p_nuevo = max(B_p * (1 - tasa_efectiva * dt / (1e9 * YR_SEC)), 1e-8)
            T_cmb_nuevo, B_gen_sup, Rm, q_conv = 0.0, 0.0, 0.0, 0.0

        if self.usar_atmosfera and self.atmosfera is not None:
            M_atm_nuevo = self.atmosfera.actualizar(t_gyr, dt, a / UA)
            atm_perdida_nueva = self.atmosfera.perdida_total
        else:
            M_atm_nuevo, atm_perdida_nueva = 0.0, False
        # ============================================================

        e_nuevo = max(e + de_dt * dt, 1e-8) if e > 1e-8 else 0.0

        return _EstadoInterno(t, a_nuevo, w_p_nuevo, B_p_nuevo, P_ram, E_p, R_m_corr,
                               tau_mag, tiempo_migracion, e=e_nuevo, Q_tidal=Q_tidal_total,
                               a_luna=a_luna_nuevo,
                               T_cmb=T_cmb_nuevo, B_gen=B_gen_sup, Rm=Rm, q_conv=q_conv,
                               M_atm=M_atm_nuevo, atm_perdida=atm_perdida_nueva,
                               eps=eps_nuevo)

    def simular(self, t_max_gyr: float = 5.0, dt_yr: float = 1000.0,
                progress_callback=None, incluir_serie: bool = True,
                max_puntos_serie: int = 2000) -> ResultadoSimulacion:

        t_max = t_max_gyr * 1e9 * YR_SEC
        dt = dt_yr * YR_SEC
        pasos = max(int(t_max / dt), 1)
        intervalo_guardado = max(pasos // max_puntos_serie, 1) if incluir_serie else None

        T_cmb_ini = self.nucleo.T_cmb if self.nucleo is not None else 0.0
        M_atm_ini_estado = self.atmosfera.M_atm if self.atmosfera is not None else 0.0

        estado = _EstadoInterno(
            t=0.0,
            a=self.parametros["a_inicial"],
            w_p=self.parametros["w_p_inicial"],
            B_p=self.parametros["B_p_inicial"],
            P_ram=0.0, E_p=0.0, R_m_norm=1.0, tau_mag=0.0, tiempo_migracion=0.0,
            e=self.e_inicial, Q_tidal=0.0,
            a_luna=self.a_luna_inicial,
            T_cmb=T_cmb_ini, B_gen=0.0, Rm=0.0, q_conv=0.0,
            M_atm=M_atm_ini_estado, atm_perdida=False,
            eps=self.eps_inicial,
        )
        inicial = estado

        serie = SerieTemporal() if incluir_serie else None
        if serie is not None:
            self._registrar_punto(serie, estado)

        for i in range(pasos):
            estado = self._paso_temporal(estado, dt)
            if serie is not None and (i % intervalo_guardado == 0 or i == pasos - 1):
                self._registrar_punto(serie, estado)
            if progress_callback and i % max(1, pasos // 100) == 0:
                progress_callback(i / pasos * 100)

        return self._construir_resultado(inicial, estado, serie)

    @staticmethod
    def _registrar_punto(serie: SerieTemporal, estado: _EstadoInterno):
        serie.tiempos.append(estado.t / (1e9 * YR_SEC))
        serie.a_ua.append(estado.a / UA)
        serie.w_p.append(estado.w_p)
        serie.B_p_gauss.append(estado.B_p * 10000)
        serie.E_p.append(estado.E_p)
        serie.R_m_norm.append(estado.R_m_norm)
        serie.tau_mag.append(estado.tau_mag)
        serie.tiempo_migracion.append(estado.tiempo_migracion)
        serie.e.append(estado.e)
        serie.Q_tidal_watts.append(estado.Q_tidal)
        serie.a_luna_ua.append(estado.a_luna / UA)
        serie.T_cmb_K.append(estado.T_cmb)
        serie.B_gen_gauss.append(estado.B_gen * 10000)  # Tesla -> Gauss
        serie.Rm_num.append(estado.Rm)
        serie.q_conv.append(estado.q_conv)
        serie.M_atm_kg.append(estado.M_atm)
        serie.atm_perdida.append(estado.atm_perdida)
        serie.eps_deg.append(np.degrees(estado.eps))

    def _construir_resultado(self, inicial: _EstadoInterno, final: _EstadoInterno,
                              serie: Optional[SerieTemporal]) -> ResultadoSimulacion:
        se_estrello = final.a < 0.01 * UA
        campo_protegido = (not se_estrello) and (final.B_p * 10000 > 0.3)

        recesion_cm_anio = 0.0
        if self.luna and final.t > 0:
            recesion_cm_anio = (final.a_luna - inicial.a_luna) / final.t * YR_SEC * 100.0

        return ResultadoSimulacion(
            nombre_planeta=self.nombre_planeta,
            a_inicial_ua=inicial.a / UA,
            a_final_ua=final.a / UA,
            w_inicial=inicial.w_p,
            w_final=final.w_p,
            B_inicial_gauss=inicial.B_p * 10000,
            B_final_gauss=final.B_p * 10000,
            P_rot_inicial_dias=2 * np.pi / abs(inicial.w_p) / (24 * 3600),
            P_rot_final_dias=2 * np.pi / abs(final.w_p) / (24 * 3600),
            E_p_final=final.E_p,
            R_m_norm_final=final.R_m_norm,
            tau_mag_final=final.tau_mag,
            tiempo_migracion_final=final.tiempo_migracion,
            campo_protegido=campo_protegido,
            se_estrello=se_estrello,
            e_inicial=inicial.e,
            e_final=final.e,
            Q_tidal_final_watts=final.Q_tidal,
            a_luna_inicial_ua=inicial.a_luna / UA,
            a_luna_final_ua=final.a_luna / UA,
            recesion_lunar_cm_anio=recesion_cm_anio,
            T_cmb_final_K=final.T_cmb,
            B_gen_final_gauss=final.B_gen * 10000,
            Rm_final=final.Rm,
            q_conv_final=final.q_conv,
            M_atm_final_kg=final.M_atm,
            atm_perdida=final.atm_perdida,
            eps_final_deg=np.degrees(final.eps),
            eps_conocido=self.eps_conocido,
            serie=serie,
        )


def simular_planeta(nombre_planeta: str, t_max_gyr: float = 5.0,
                     dt_yr: float = 1000.0, callback=None,
                     estrellas: Optional[Dict] = None,
                     planetas: Optional[Dict] = None,
                     incluir_serie: bool = True,
                     max_puntos_serie: int = 2000,
                     parametros_extra: Optional[Dict] = None,
                     estrella_personalizada: Optional[Dict] = None,
                     lunas_personalizadas: Optional[Dict] = None) -> ResultadoSimulacion:
    motor = MotorMHD(
        nombre_planeta,
        parametros_extra=parametros_extra,
        estrellas=estrellas,
        planetas_db=planetas,
        lunas=None,
        estrella_personalizada=estrella_personalizada,
        lunas_personalizadas=lunas_personalizadas
    )
    return motor.simular(t_max_gyr, dt_yr, callback, incluir_serie, max_puntos_serie)
