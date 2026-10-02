import numpy as np
from typing import Dict, Optional
import warnings
from progreso_util import invocar_callback  # Sugerencia 4: logs en vivo (fracción 0-1 + mensaje opcional)

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


R_SOL = 6.957e8
Q_ESTRELLA_DEFECTO = 1.0e7  # Q' estelar modificado (Penev et al. 2018; con 1e6 K2-141 b y TOI-2431 b
                            # caerian en < 10 Myr, incompatible con sistemas de varios Gyr)


def estimar_R_estrella(masa_estrella_kg: float) -> float:
    """Radio estelar de secuencia principal estimado por la masa (m).
    AUDITORIA oct-2026: la base no guarda radios estelares; relacion
    masa-radio R/Rsol = M^0.9 (M<1 Msol; enanas K/M, cf. Boyajian et al.
    2012) o M^0.57 (M>=1 Msol). Error tipico < 10 % en radio."""
    m = max(masa_estrella_kg / M_SOL, 0.05)
    return R_SOL * (m ** 0.9 if m < 1.0 else m ** 0.57)


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
                 "tiempo_migracion", "e", "Q_tidal", "a_lunas",
                 "T_cmb", "B_gen", "Rm", "q_conv", "M_atm", "atm_perdida", "eps"]

    def __init__(self, t, a, w_p, B_p, P_ram, E_p, R_m_norm, tau_mag, tiempo_migracion,
                 e=0.0, Q_tidal=0.0, a_lunas=None,
                 T_cmb=0.0, B_gen=0.0, Rm=0.0, q_conv=0.0, M_atm=0.0, atm_perdida=False,
                 eps=0.0):
        self.t, self.a, self.w_p, self.B_p = t, a, w_p, B_p
        self.P_ram, self.E_p, self.R_m_norm = P_ram, E_p, R_m_norm
        self.tau_mag, self.tiempo_migracion = tau_mag, tiempo_migracion
        self.e, self.Q_tidal = e, Q_tidal
        # NUEVO (multi-luna, ago-2026): lista de distancias orbitales, una
        # por luna en self.lunas (mismo orden). Antes era un escalar
        # "a_luna" (una sola luna posible). Lista vacía si el planeta no
        # tiene lunas -- nunca None, para no tener que chequear en cada
        # sitio que la usa.
        self.a_lunas = list(a_lunas) if a_lunas is not None else []
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
        F_XUV = self.parametros.get("F_XUV_inicial", 0.005)  # AUDITORIA oct-2026: antes 1.0 W/m2 (200x el Sol en calma)
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

        # NUEVO (multi-luna, ago-2026): self.lunas es SIEMPRE una lista
        # (posiblemente vacía). Compatibilidad hacia atrás: si lunas_db
        # trae el formato viejo (un solo dict, no lista -- por ejemplo un
        # archivo de sesión .mhd guardado antes de este cambio), se
        # envuelve en una lista de un elemento en vez de fallar.
        entrada_lunas = self.lunas_db.get(nombre_planeta, [])
        if isinstance(entrada_lunas, dict):
            entrada_lunas = [entrada_lunas]
        self.lunas = list(entrada_lunas)
        self.a_lunas_inicial = [float(l["a_luna_inicial"]) for l in self.lunas]

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
        # --------------------------------------------------------------
        # NUEVO FASE 1: torque atmosferico gravitatorio-termico
        # --------------------------------------------------------------
        self.torque_atmosferico_on = self.parametros.get("torque_atmosferico", False)
        self.K_atm_vis = float(self.parametros.get("K_atm_vis", 0.0))
        self.K_atm_term = float(self.parametros.get("K_atm_term", 0.0))
        self.tau_rad_atm_s = float(self.parametros.get("tau_rad_atm_s", 3.0e5))
        self.atm_rho_norm = float(self.parametros.get("atm_rho_norm", 1.0e4))
        self.w_atm_eq = self.parametros.get("w_atm_eq", None)
        self.w_atm_eq_mode = self.parametros.get("w_atm_eq_mode", "retrograde_sync")
        self.atm_lag_model = self.parametros.get("atm_lag_model", "sin2delta")
        self.M_atm_fija = float(self.parametros.get(
            "M_atm", self.parametros.get("M_atm_inicial", 0.0)))


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

        # AUDITORIA oct-2026 (bug de migracion): decaimiento orbital por la
        # marea que el PLANETA levanta en la ESTRELLA (Q' estelar), no por la
        # marea del planeta. Ver _evolucion_orbital_marea_estelar().
        self.R_estrella = float(self.parametros.get("R_estrella_m", estimar_R_estrella(self.M_estrella)))
        self.Q_estrella = float(self.parametros.get("Q_estrella", Q_ESTRELLA_DEFECTO))

    def _evolucion_orbital_marea_estelar(self, a: float, dt: float, w_estrella: float):
        """AUDITORIA oct-2026. Decaimiento (o expansion) orbital por la marea
        que el planeta levanta en la estrella (Goldreich & Soter 1966;
        Jackson et al. 2009; Penev et al. 2018):

            da/dt = -s * (9/2) * (M_p/M*) * (R*/a)^5 * n * a / Q'*

        con s = +1 si la estrella gira mas lento que la orbita (el planeta
        cae) y s = -1 si gira mas rapido (el planeta se aleja). Como
        a^(13/2) evoluciona linealmente en el tiempo, se integra de forma
        EXACTA (sin Euler): el resultado no depende de dt y no hay
        sobrepaso. Devuelve (a_nuevo, tiempo_caracteristico_s)."""
        n = np.sqrt(G * self.M_estrella / a ** 3)
        s = 1.0 if abs(w_estrella) < n else -1.0
        K = 4.5 * (self.M / self.M_estrella) * (self.R_estrella ** 5) * np.sqrt(G * self.M_estrella) / self.Q_estrella
        dadt = -s * K * a ** (-5.5)
        tau = a / abs(dadt) if dadt != 0.0 else 1e30
        x = a ** 6.5 - s * 6.5 * K * dt
        if x <= self.a_colapso ** 6.5:
            return self.a_colapso, tau
        return float(x ** (1.0 / 6.5)), float(tau)

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

    def calcular_torque_lunar(self, luna: dict, a_luna: float, w_p: float) -> float:
        """Torque de marea de UNA luna sobre la rotación del planeta."""
        if a_luna <= 0:
            return 0.0
        M_luna = luna["masa"]
        k2 = luna["k2"]
        Q_p = luna["Q_p"]
        n_luna = np.sqrt(G * self.M / a_luna ** 3)
        tau_magnitud = 1.5 * (k2 / Q_p) * G * (M_luna ** 2) * (self.R_p ** 5) / (a_luna ** 6)
        delta = w_p - n_luna
        if delta > 0:
            return -tau_magnitud
        elif delta < 0:
            return tau_magnitud
        else:
            return 0.0

    def calcular_recesion_lunar(self, luna: dict, a_luna: float, tau_lunar: float) -> float:
        """Recesión/decaimiento orbital de UNA luna, dado el torque que actúa sobre ella."""
        if a_luna <= 0:
            return 0.0
        M_luna = luna["masa"]
        factor = 0.5 * M_luna * np.sqrt(G * self.M / a_luna)
        if factor == 0:
            return 0.0
        return -tau_lunar / factor

    def _evolucion_lunas(self, a_lunas: list, w_p: float, dt: float,
                          incluir_torque_en_wp: bool,
                          max_frac_cambio: float = 0.0003, max_subpasos: int = 150000):
        """
        Evolución CONJUNTA y sub-paso de {w_p, a_lunas} debida SOLO al
        torque lunar, sobre un intervalo dt. Devuelve (a_lunas_nuevo,
        w_p_nuevo). El resto de los torques (magnético, marea estelar,
        atmosférico) NO pasan por acá -- _paso_temporal los aplica antes,
        con un paso de Euler simple sobre dt como siempre, y el w_p
        resultante de eso es el `w_p` que se le pasa a esta función como
        punto de partida (ver _paso_temporal).

        FIX (paso adaptativo lunar, ago-2026) -- POR QUÉ w_p Y a_lunas
        SE SUBDIVIDEN JUNTOS: una primera versión de este fix subdividía
        SOLO a_lunas (dejando w_p con su Euler grueso de siempre, usando
        el tau_lunar PROMEDIADO de los sub-pasos). Se probó contra los
        casos ya documentados como inestables y w_p seguía disparándose
        a valores imposibles -- el promedio de tau_lunar sobre el
        intervalo puede seguir siendo enorme si a_luna pasó cerca del
        planeta en algún sub-paso, y aplicarlo con un solo Euler grueso
        sobre TODO dt igual desestabiliza w_p. La solución real es
        subdividir tau_lunar -> w_p exactamente con la misma grilla fina
        que a_lunas, sub-paso a sub-paso.

        CRITERIO DE SUB-PASOS -- por fracción de cambio de a_luna, NO
        por período orbital: se descartó un criterio tipo CFL basado en
        el período orbital de la luna (mismo espíritu que dt_sugerido en
        n_cuerpos_ligero_optimizado.py) porque para una luna real
        (período de días) contra un dt exterior típico de 10.000 años
        pedía millones de sub-pasos -- inviable, y el techo de seguridad
        lo hubiera dejado en miles de sub-pasos SIEMPRE, para TODO
        planeta con luna, incluida la Tierra. No importa resolver la
        fase orbital rápida de la luna (el motor no la trackea, solo el
        semieje a_luna que evoluciona LENTO por marea) -- importa que
        a_luna no cambie más de `max_frac_cambio` (0.03%) en un sub-paso.
        En el caso normal (Luna real, galileanas...) esa fracción es
        minúscula (~1e-6 por paso de 10.000 años), así que n_subpasos=1
        y CERO costo extra sobre el comportamiento de antes -- verificado
        con pruebas de regresión (Tierra, Júpiter dan resultados idénticos
        al bit antes/después de este cambio).

        max_subpasos pone un techo al costo computacional para casos
        realmente extremos (luna casi rozando el planeta) -- en ese
        límite el resultado deja de estar totalmente resuelto, pero el
        chequeo de estabilidad de sintetico_ui.py (w_final > 1e-2 rad/s)
        sigue funcionando como red de seguridad para avisar.

        incluir_torque_en_wp: refleja self.torque_lunar_on -- si está
        apagado, a_lunas evoluciona igual (proceso físico separado, ver
        nota de Mejora 4 en _paso_temporal) pero w_p sale sin cambios.

        NOTA: no hay interacción gravitatoria entre lunas (ej. resonancias
        de Laplace entre Io/Europa/Ganímedes) -- cada luna evoluciona de
        forma independiente por marea con el planeta, igual que en el
        modelo de una sola luna. Añadir esa interacción es trabajo aparte
        (Fase 1.3 del plan v6.0, sección "interacción gravitatoria entre
        lunas -- opcional"), no incluido acá.
        """
        if not self.lunas or dt <= 0:
            return list(a_lunas), w_p

        n_subpasos = 1
        for luna, a_luna in zip(self.lunas, a_lunas):
            if a_luna <= 0:
                continue
            tau_l0 = self.calcular_torque_lunar(luna, a_luna, w_p)
            da_dt0 = self.calcular_recesion_lunar(luna, a_luna, tau_l0)
            frac_cambio = abs(da_dt0 * dt / a_luna)
            if frac_cambio > max_frac_cambio:
                n_subpasos = max(n_subpasos, int(np.ceil(frac_cambio / max_frac_cambio)))
        n_subpasos = min(n_subpasos, max_subpasos)

        dt_sub = dt / n_subpasos
        a_lunas_actual = list(a_lunas)
        w_p_actual = w_p
        for _ in range(n_subpasos):
            tau_lunar_paso = 0.0
            a_lunas_siguiente = []
            for luna, a_luna in zip(self.lunas, a_lunas_actual):
                tau_l = self.calcular_torque_lunar(luna, a_luna, w_p_actual)
                da_luna_dt = self.calcular_recesion_lunar(luna, a_luna, tau_l)
                a_lunas_siguiente.append(max(a_luna + da_luna_dt * dt_sub, self.R_p))
                tau_lunar_paso += tau_l
            a_lunas_actual = a_lunas_siguiente
            if incluir_torque_en_wp:
                w_p_actual = w_p_actual + (tau_lunar_paso / self.I) * dt_sub
                # mismo piso que en _paso_temporal para evitar division
                # por cero mas adelante en el motor (E_p, etc.)
                if abs(w_p_actual) < 1e-20:
                    w_p_actual = 1e-20 if w_p_actual >= 0 else -1e-20

        return a_lunas_actual, w_p_actual

    # ------------------------------------------------------------------
    # NUEVO FASE 1: torque atmosferico gravitatorio-termico
    # ------------------------------------------------------------------
    def calcular_torque_atmosferico_termico(self, estado, w_p, n):
        if not self.torque_atmosferico_on:
            return 0.0
        # AUDITORIA oct-2026: con el modelo de atmosfera activo, una
        # atmosfera perdida (M_atm=0) ya no vuelve a la masa inicial.
        if self.usar_atmosfera:
            M_atm = estado.M_atm
        else:
            M_atm = self.M_atm_fija
        if M_atm <= 0.0:
            return 0.0
        rho_col = M_atm / (4.0 * np.pi * self.R_p ** 2)
        rho_norm = rho_col / max(self.atm_rho_norm, 1e-12)
        a_ua = max(estado.a / UA, 1e-6)
        m_star = self.M_estrella / M_SOL
        alpha_vis = -self.K_atm_vis * w_p * rho_norm * (a_ua ** -2) * m_star
        if self.w_atm_eq is not None:
            w_eq = float(self.w_atm_eq)
        else:
            w_eq = 0.0 if self.w_atm_eq_mode == "zero" else -abs(n)
        if self.tau_rad_atm_s <= 0.0 or self.K_atm_term == 0.0:
            return self.I * alpha_vis
        x = (w_p - w_eq) * self.tau_rad_atm_s
        if self.atm_lag_model == "tanh":
            lag = float(np.tanh(x))
        else:
            lag = (2.0 * x) / (1.0 + x * x) if abs(x) <= 1e12 else 0.0
        alpha_term = -self.K_atm_term * lag * rho_norm * (a_ua ** -3) * m_star
        return self.I * (alpha_vis + alpha_term)



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

        # AUDITORIA oct-2026: migracion por marea ESTELAR, integrada exacta
        # (antes: formula de circularizacion con marea del planeta y Euler
        # explicito -> 91/300 planetas caian a la estrella y dependia de dt).
        if self.colapsado:
            a_migr, tiempo_migracion = self.a_colapso, 0.0
        else:
            a_migr, tiempo_migracion = self._evolucion_orbital_marea_estelar(a, dt, w_estrella_t)

        a_lunas = estado.a_lunas
        # NOTA (Mejora 4, ahora multi-luna): la evolución orbital de las
        # lunas se calcula siempre, independiente del toggle
        # torque_lunar_on -- ese toggle aísla el efecto del torque lunar
        # sobre la ROTACIÓN del planeta (para depuración/didáctica); la
        # evolución orbital de las lunas en sí es un proceso físico
        # separado que no tiene sentido apagar a medias.
        #
        # FIX (paso adaptativo lunar, ago-2026): el torque lunar y su
        # efecto en w_p ahora se calculan DESPUÉS de los demás torques
        # (ver más abajo, tras armar tau_otros) -- _evolucion_lunas hace
        # su propio sub-paso interno acoplando w_p y a_lunas juntos. Acá
        # arriba solo queda la nota de contexto; el cálculo real se
        # movió después de tau_atm para tener tau_otros disponible.

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
        tau_atm = self.calcular_torque_atmosferico_termico(estado, w_p, n)

        # --------------------------------------------------------------
        # MEJORA v4.1 (experimentos controlados): cada torque se suma solo
        # si su flag está activa. Con las 3 en True (default) el resultado
        # es idéntico a antes de esta mejora.
        #
        # FIX (paso adaptativo lunar, ago-2026): tau_lunar SALIÓ de esta
        # suma -- antes tau_total incluía tau_lunar y todo w_p se
        # integraba junto en un solo Euler grueso sobre dt, lo que podía
        # desestabilizarse con lunas cercanas/masivas (ver docstring de
        # _evolucion_lunas). Ahora: 1) se integra w_p con los torques
        # "otros" (magnético, marea estelar, atmosférico) con Euler
        # grueso como siempre -- CERO cambio de comportamiento para
        # planetas sin lunas problemáticas; 2) recién con ese w_p ya
        # actualizado, _evolucion_lunas aplica el torque lunar en sus
        # propios sub-pasos, acoplado con a_lunas.
        # --------------------------------------------------------------
        tau_otros = 0.0
        if self.torque_magnetico_on:
            tau_otros += tau_mag * R_ohm
        if self.torque_marea_estelar_on:
            tau_otros += tau_tide_star
        if self.torque_atmosferico_on:
            tau_otros += tau_atm

        dw_p_dt_otros = tau_otros / self.I
        w_p_tras_otros = w_p + dw_p_dt_otros * dt
        # AUDITORIA oct-2026 (bug de rotacion): el torque de marea estelar es
        # de magnitud fija con signo (w - n); con Euler explicito sobrepasaba
        # la sincronia y oscilaba (TRAPPIST-1e terminaba en 1.3-80 dias segun
        # dt, a veces retrogrado). Si en este paso la rotacion CRUZA n por
        # efecto de la marea, el planeta queda en rotacion sincronica
        # (bloqueo de marea), que es el estado fisico de equilibrio.
        if self.torque_marea_estelar_on and tau_tide_star != 0.0:
            if (w_p - n) * (w_p_tras_otros - n) < 0.0:
                w_p_tras_otros = n
        if abs(w_p_tras_otros) < 1e-20:
            if tau_otros < 0.0:
                w_p_tras_otros = -1e-20
            elif tau_otros > 0.0:
                w_p_tras_otros = 1e-20
            else:
                w_p_tras_otros = 1e-20

        a_lunas_nuevo_tmp, w_p_nuevo = self._evolucion_lunas(
            a_lunas, w_p_tras_otros, dt, incluir_torque_en_wp=self.torque_lunar_on
        )
        if abs(w_p_nuevo) < 1e-20:
            w_p_nuevo = 1e-20 if w_p_nuevo >= 0 else -1e-20

        a_nuevo = a_migr
        if a_nuevo <= self.a_colapso:
            self.colapsado = True
        a_lunas_nuevo = a_lunas_nuevo_tmp

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
                               a_lunas=a_lunas_nuevo,
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

        # AUDITORIA oct-2026: limite de colapso = el mayor entre el radio
        # estelar y el limite de Roche fluido del planeta, 2.44 R_p (M*/M_p)^(1/3).
        self.a_colapso = max(self.R_estrella,
                             2.44 * self.R_p * (self.M_estrella / max(self.M, 1.0)) ** (1.0 / 3.0))
        self.colapsado = False

        T_cmb_ini = self.nucleo.T_cmb if self.nucleo is not None else 0.0
        M_atm_ini_estado = self.atmosfera.M_atm if self.atmosfera is not None else 0.0

        estado = _EstadoInterno(
            t=0.0,
            a=self.parametros["a_inicial"],
            w_p=self.parametros["w_p_inicial"],
            B_p=self.parametros["B_p_inicial"],
            P_ram=0.0, E_p=0.0, R_m_norm=1.0, tau_mag=0.0, tiempo_migracion=0.0,
            e=self.e_inicial, Q_tidal=0.0,
            a_lunas=self.a_lunas_inicial,
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
                frac = i / pasos
                invocar_callback(progress_callback, frac, f"Integrando órbita... paso {i}/{pasos} ({frac*100:.0f}%)")

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
        # a_luna_ua sigue describiendo SOLO la primera luna (compatibilidad
        # con SerieTemporal/exportar_video.py/exportar_csv.py, que asumen
        # una sola columna de distancia lunar). Para el detalle de todas
        # las lunas, ver ResultadoSimulacion.lunas (resumen final, no serie
        # temporal completa por ahora -- ver nota en _construir_resultado).
        serie.a_luna_ua.append((estado.a_lunas[0] / UA) if estado.a_lunas else 0.0)
        # NUEVO (multi-luna, viz 3D, ago-2026): serie completa, todas las
        # lunas por paso de tiempo -- ver nota en models.py SerieTemporal.
        serie.a_lunas_ua.append([a / UA for a in estado.a_lunas])
        serie.T_cmb_K.append(estado.T_cmb)
        serie.B_gen_gauss.append(estado.B_gen * 10000)  # Tesla -> Gauss
        serie.Rm_num.append(estado.Rm)
        serie.q_conv.append(estado.q_conv)
        serie.M_atm_kg.append(estado.M_atm)
        serie.atm_perdida.append(estado.atm_perdida)
        serie.eps_deg.append(np.degrees(estado.eps))

    def _construir_resultado(self, inicial: _EstadoInterno, final: _EstadoInterno,
                              serie: Optional[SerieTemporal]) -> ResultadoSimulacion:
        # AUDITORIA oct-2026: antes era un umbral fijo a < 0.01 UA, que
        # marcaba como estrellados a planetas reales que orbitan dentro de
        # 0.01 UA (GJ 367 b, K2-141 b, TOI-2431 b, Kepler-42 c).
        se_estrello = bool(self.colapsado or final.a <= self.a_colapso * 1.000001)
        campo_protegido = (not se_estrello) and (final.B_p * 10000 > 0.3)

        # --------------------------------------------------------------
        # Multi-luna (ago-2026): resumen por luna, calculado para TODAS
        # las lunas de self.lunas. Los campos escalares a_luna_*/
        # recesion_lunar_cm_anio de abajo se mantienen apuntando a la
        # PRIMERA luna (índice 0) -- compatibilidad con CSV/JSON/UI
        # existentes, que solo conocen "una luna". El detalle completo
        # (todas las lunas) vive en resultado.lunas.
        # --------------------------------------------------------------
        lunas_resumen = []
        for i, luna in enumerate(self.lunas):
            a_ini_i = inicial.a_lunas[i]
            a_fin_i = final.a_lunas[i]
            recesion_i = ((a_fin_i - a_ini_i) / final.t * YR_SEC * 100.0) if final.t > 0 else 0.0
            lunas_resumen.append({
                "nombre": luna.get("nombre", f"Luna_{i+1}"),
                "masa_kg": luna["masa"],
                "a_inicial_ua": a_ini_i / UA,
                "a_final_ua": a_fin_i / UA,
                "recesion_cm_anio": recesion_i,
            })

        a_luna_inicial_ua = lunas_resumen[0]["a_inicial_ua"] if lunas_resumen else 0.0
        a_luna_final_ua = lunas_resumen[0]["a_final_ua"] if lunas_resumen else 0.0
        recesion_cm_anio = lunas_resumen[0]["recesion_cm_anio"] if lunas_resumen else 0.0

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
            a_luna_inicial_ua=a_luna_inicial_ua,
            a_luna_final_ua=a_luna_final_ua,
            recesion_lunar_cm_anio=recesion_cm_anio,
            lunas=lunas_resumen,
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
