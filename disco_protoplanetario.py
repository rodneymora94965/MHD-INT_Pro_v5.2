"""
disco_protoplanetario.py
MHD-INT v5.9 (módulo de extensión, MODO SINTÉTICO)

Evolución de la desalineación estelar-disco (β: ángulo entre el eje de
spin de una estrella joven y el eje de su disco protoplanetario) por
acoplamiento magnético + de acreción disco-estrella.

REESCRITURA COMPLETA (auditoría 2026-08-09): las versiones anteriores de
este módulo reconstruían la física a partir de una descripción de segunda
mano (la propuesta original). Esa reconstrucción acumuló 4 errores reales
encontrados y corregidos en auditorías previas (fórmula de torque
magnético sin respaldo directo, conversión CGS->SI de R_t, radio estelar
de secuencia principal en vez de pre-secuencia-principal, combinación de
tasas vs. tiempos característicos) antes de llegar a la fuente primaria.

Esta versión implementa DIRECTAMENTE la Ecuación 23 de Lai, Foucart & Lin
(2011, MNRAS 412, 2790, arXiv:1008.3148), sin intermediarios:

    d(cos β)/dt = (N₀/J*) · sin²β · (λ − ζ̃·cos²β)

donde:
    β    = ángulo de desalineación spin-disco (la cantidad física real)
    N₀   = Ṁ·√(G·M*·r_in)          [escala de torque de acreción, Ec. 1]
    J*   = 0.2·M*·R*²·Ω*           [momento angular de spin estelar]
    r_in = η·(μ⁴/(G·M*·Ṁ²))^(1/7)  [radio de truncamiento magnetosférico]
    μ    = B*·R*³                  [momento dipolar magnético]
    η    ~ 0.5 (factor de orden unidad, Ghosh & Lamb 1979 / Bessolaz 2008)

λ Y ζ̃ SON LOS PARÁMETROS QUE REALMENTE CONTROLAN EL RESULTADO — no B, no
M_disco, no radio de disco. El propio Lai, Foucart & Lin (2011) los
describe como "en gran medida sin restringir" (largely unconstrained):
- λ (torque de acreción, tiende a ALINEAR): rango sugerido ~0.1-1
- ζ̃ (torque de "warping" magnético, tiende a DESALINEAR): orden ~1-varios

COMPORTAMIENTO CUALITATIVO (esto es lo que hace este mecanismo realmente
interesante, y lo que las versiones anteriores de este módulo no podían
capturar):
- Si ζ̃/λ < 1: β=0 es el único equilibrio estable. Cualquier desalineación
  primordial decae hacia la alineación.
- Si ζ̃/λ > 1: β=0 se vuelve INESTABLE. El sistema evoluciona hacia un
  equilibrio en β₊ = arccos(√(λ/ζ̃)), o hacia retrógrado completo (~180°)
  si la desalineación inicial ya era grande. Es decir: el mecanismo puede
  GENERAR desalineación desde casi-cero, no solo preservarla.

QUÉ NO HACE ESTE MÓDULO: no predice un ángulo único y determinista para
una estrella real a partir de B/masa del disco/etc. — porque la teoría
real tampoco lo hace. λ y ζ̃ deben elegirse (con las guías de rango de
arriba), no calcularse desde primeros principios. Cualquier UI que use
este módulo debe dejar eso explícito, no implícito.

VALIDACIÓN PARCIAL (2026-08-08, sigue vigente en esta reescritura porque
r_in no cambió): r_in calculado para DO Tau = 0.0122 UA (1.32 R*) vs.
publicado 0.014 UA (1.6 R*), Bessolaz et al. 2008 — dentro de ~15%. Esto
valida SOLO el radio de truncamiento, no la evolución de β completa (no
existe una estrella con β medido con precisión suficiente para validar
eso — ver evaluación del catálogo de 15 estrellas T Tauri, 2026-08-09:
solo TW Hya tiene un indicio indirecto y con incertidumbre considerable,
que además mezcla inclinación de disco, inclinación de spin, y oblicuidad
magnética dipolo-spin — tres cantidades DISTINTAS de β).

NO TOCA engine.py, termica.py, atmosfera.py, numba_functions.py — módulo
completamente independiente del motor de simulación planetaria.
"""

import numpy as np

# ============================================================================
# CONSTANTES (SI, mismas convenciones que el resto de MHD-INT)
# ============================================================================
YR_SEC = 365.25 * 24 * 3600
G = 6.674e-11
M_SOL = 1.98847e30
R_SOL = 6.957e8
GAUSS_A_TESLA = 1.0e-4
UA = 1.495978707e11

# Rangos sugeridos por Lai, Foucart & Lin (2011) para lambda y zeta_tilde.
# NO son valores medidos ni calibrados -- son el rango de plausibilidad
# que el propio paper sugiere como punto de partida razonable.
LAMBDA_RANGO_SUGERIDO = (0.1, 1.0)
ZETA_TILDE_RANGO_SUGERIDO = (0.5, 3.0)


class DiscoProtoplanetario:
    """
    Evoluciona la desalineación spin-disco (beta) de una estrella joven,
    implementando directamente la Ecuacion 23 de Lai, Foucart & Lin (2011).

    Parametros
    ----------
    M_estrella_msol, R_estrella_rsol : float
        Masa y radio de la estrella (masas/radios solares). El radio se
        toma como INPUT directo (no derivado de una relacion masa-radio)
        porque para estrellas T Tauri reales catalogadas, el radio ya es
        un dato medido/estimado especifico de cada estrella.
    B_estrella_gauss : float
        Campo magnetico superficial, en Gauss.
    P_rot_dias : float
        Periodo de rotacion estelar, en dias.
    Mdot0_msol_yr : float
        Tasa de acrecion de masa disco->estrella AL INICIO, en M_sol/año.
        Se asume que decae junto con el disco (ver _mdot(t)).
    tau_disco_myr : float
        Tiempo caracteristico de disipacion exponencial del disco/acrecion,
        en Myr.
    lam : float
        Parametro adimensional del torque de acrecion (alineador). NO
        calculado -- elegido dentro del rango sugerido por el paper
        (ver LAMBDA_RANGO_SUGERIDO). Este es el parametro de mayor
        incertidumbre del modulo completo.
    zeta_tilde : float
        Parametro adimensional del torque de warping magnetico
        (desalineador). Mismo comentario que lam (ver
        ZETA_TILDE_RANGO_SUGERIDO).
    beta_inicial_deg : float
        Desalineacion inicial, en grados. Default 1.0 (casi alineado,
        estado post-colapso tipico).
    """

    def __init__(self, M_estrella_msol, R_estrella_rsol, B_estrella_gauss,
                 P_rot_dias, Mdot0_msol_yr, tau_disco_myr, lam, zeta_tilde,
                 beta_inicial_deg=1.0):
        self.M_estrella = M_estrella_msol * M_SOL
        self.R_estrella = R_estrella_rsol * R_SOL
        self.B_estrella = B_estrella_gauss * GAUSS_A_TESLA
        self.Omega_estrella = 2 * np.pi / (P_rot_dias * 86400.0)
        self.Mdot0 = Mdot0_msol_yr * M_SOL / YR_SEC
        self.tau_disco = tau_disco_myr * 1.0e6 * YR_SEC
        self.lam = lam
        self.zeta_tilde = zeta_tilde

        # Momento angular de spin estelar, J* = 0.2 M R^2 Omega (Lai 2011)
        self.J_estrella = 0.2 * self.M_estrella * self.R_estrella ** 2 * self.Omega_estrella

        # Momento dipolar: mu = B * R^3
        self.mu_estrella = self.B_estrella * self.R_estrella ** 3

        self.beta = np.radians(max(beta_inicial_deg, 1e-3))
        self.historial = {"t_myr": [], "beta_deg": [], "Mdot_msol_yr": [], "r_in_ua": []}

    def _mdot(self, t_seg):
        """Tasa de acrecion en el tiempo t, decayendo junto con el disco."""
        return self.Mdot0 * np.exp(-t_seg / self.tau_disco)

    def _radio_truncamiento(self, Mdot):
        """r_in = eta * (mu^4 / (G*M*Mdot^2))^(1/7)  [Ec. 1, Lai et al. 2011]

        Calculado en CGS-Gaussiano (como esta publicado, sin ambiguedad de
        mu0) y convertido a metros al final. Validado contra DO Tau."""
        eta = 0.5
        if Mdot <= 0:
            return self._radio_corrotacion()

        G_cgs = 6.674e-8
        R_cm = self.R_estrella * 100.0
        M_g = self.M_estrella * 1000.0
        Mdot_g_s = Mdot * 1000.0
        B_gauss = self.B_estrella / GAUSS_A_TESLA
        mu_cgs = B_gauss * R_cm ** 3

        r_in_cm = eta * (mu_cgs ** 4 / (G_cgs * M_g * Mdot_g_s ** 2)) ** (1.0 / 7.0)
        return r_in_cm / 100.0

    def _radio_corrotacion(self):
        return (G * self.M_estrella / self.Omega_estrella ** 2) ** (1.0 / 3.0)

    def evolucionar(self, t_total_myr, n_pasos=4000):
        """Integra d(cos beta)/dt (Ec. 23) desde t=0 hasta t_total_myr.
        Devuelve (beta_final_deg, historial)."""
        t_total_seg = t_total_myr * 1.0e6 * YR_SEC
        dt = t_total_seg / n_pasos

        cos_beta = np.cos(self.beta)
        r_in0 = self._radio_truncamiento(self.Mdot0)
        self.historial = {"t_myr": [0.0], "beta_deg": [np.degrees(self.beta)],
                           "Mdot_msol_yr": [self.Mdot0 * YR_SEC / M_SOL],
                           "r_in_ua": [r_in0 / UA]}

        t = 0.0
        MDOT_MINIMO = self.Mdot0 * 1e-6
        for _ in range(n_pasos):
            Mdot = self._mdot(t)
            if Mdot < MDOT_MINIMO:
                t += dt
                self.historial["t_myr"].append(t / (1.0e6 * YR_SEC))
                self.historial["beta_deg"].append(np.degrees(np.arccos(np.clip(cos_beta, -1, 1))))
                self.historial["Mdot_msol_yr"].append(0.0)
                self.historial["r_in_ua"].append(self.historial["r_in_ua"][-1])
                continue

            r_in = self._radio_truncamiento(Mdot)
            N0 = Mdot * np.sqrt(G * self.M_estrella * r_in)

            sin2_beta = max(1.0 - cos_beta ** 2, 0.0)
            d_cosbeta_dt = (N0 / self.J_estrella) * sin2_beta * (self.lam - self.zeta_tilde * cos_beta ** 2)

            cos_beta += d_cosbeta_dt * dt
            cos_beta = min(max(cos_beta, -1.0), 1.0)

            t += dt
            self.historial["t_myr"].append(t / (1.0e6 * YR_SEC))
            self.historial["beta_deg"].append(np.degrees(np.arccos(cos_beta)))
            self.historial["Mdot_msol_yr"].append(Mdot * YR_SEC / M_SOL)
            self.historial["r_in_ua"].append(r_in / UA)

        self.beta = np.arccos(cos_beta)
        beta_final_deg = np.degrees(self.beta)
        return beta_final_deg, self.historial

    def equilibrio_esperado(self):
        """Calcula el/los equilibrio(s) analitico(s) de la Ec. 23, para
        contrastar contra el resultado numerico de evolucionar().
        beta=0 siempre es un punto fijo. Si zeta_tilde/lam > 1, aparece un
        segundo equilibrio ESTABLE en beta_plus, y beta=0 se vuelve
        inestable."""
        if self.zeta_tilde <= 0:
            return {"beta_0_estable": True, "beta_plus_deg": None}
        razon = self.lam / self.zeta_tilde
        if razon >= 1.0:
            return {"beta_0_estable": True, "beta_plus_deg": None}
        beta_plus = np.degrees(np.arccos(np.sqrt(razon)))
        return {"beta_0_estable": False, "beta_plus_deg": beta_plus}

    @staticmethod
    def validar_radio_truncamiento_contra_do_tau():
        """Chequeo de sanity check contra un caso real publicado: DO Tau
        (Bessolaz et al. 2008, valores actualizados via SPIRou 2026).
        r_in medido = 1.6 +/- 0.3 R* = 0.014 +/- 0.002 UA.
        Valida SOLO r_in, no la evolucion de beta completa."""
        d = DiscoProtoplanetario(
            M_estrella_msol=0.7, R_estrella_rsol=2.0, B_estrella_gauss=250,
            P_rot_dias=5.0, Mdot0_msol_yr=10 ** -7.6, tau_disco_myr=3.0,
            lam=0.5, zeta_tilde=1.0,
        )
        r_in = d._radio_truncamiento(d.Mdot0)
        r_in_ua = r_in / UA
        r_in_sobre_Rstar = r_in / d.R_estrella
        print(f"r_in calculado = {r_in_ua:.4f} UA ({r_in_sobre_Rstar:.2f} R*)")
        print(f"r_in publicado (DO Tau) = 0.014 UA (1.6 R*)")
        return r_in_ua, r_in_sobre_Rstar

    def advertencia_parametros_asumidos(self):
        """Mensaje que SIEMPRE debe mostrarse en la UI junto a cualquier
        resultado de este modulo (no condicional): lambda/zeta_tilde son
        elegidos, no derivados."""
        return (
            f"λ={self.lam:.2f} y ζ̃={self.zeta_tilde:.2f} son valores ASUMIDOS "
            f"dentro del rango que Lai, Foucart & Lin (2011) sugieren como "
            f"plausible (λ~{LAMBDA_RANGO_SUGERIDO[0]}-{LAMBDA_RANGO_SUGERIDO[1]}, "
            f"ζ̃~{ZETA_TILDE_RANGO_SUGERIDO[0]}-{ZETA_TILDE_RANGO_SUGERIDO[1]}), "
            f"no derivados de B/masa del disco/etc. El propio paper los "
            f"describe como 'en gran medida sin restringir'. Este resultado "
            f"es una exploración de un escenario plausible, no una predicción "
            f"única para esta estrella."
        )
