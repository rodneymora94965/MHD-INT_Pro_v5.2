"""
Tests de regresion de la auditoria del motor (oct-2026).

Cada test cubre un bug encontrado y corregido en esa auditoria, para que
no vuelva a aparecer sin que nadie se entere:

  1. Migracion orbital dependiente del paso dt (91 de 300 planetas se
     "estrellaban").                       -> test_migracion_*
  2. Rotacion que oscilaba alrededor de la sincronia por la marea
     estelar (P_rot dependia de dt).       -> test_rotacion_*
  3. se_estrello con umbral fijo de 0.01 UA. -> test_no_se_estrella_*
  4. Flujo XUV escalado dos veces con la distancia (a^-4). -> test_xuv_*
  5. Torque atmosferico que volvia a la masa inicial al perder la
     atmosfera.                            -> test_torque_atm_*
  6. Penalizacion de oblicuidad < 5 grados sin base fisica.
                                           -> test_oblicuidad_*
  7. Datos corregidos (GJ 1132 b, LHS 475 b, GJ 3293 b, HD 27894).
                                           -> test_datos_*

Para correr solo estos:
    pytest tests/test_auditoria_oct2026.py -v
"""
import math

import pytest

from atmosfera import Atmosfera
from database import PLANETAS
from engine import MotorMHD, UA, simular_planeta
from habitabilidad import calcular_mhi

T_GYR = 1.0  # suficiente para llegar al equilibrio de marea en planetas cercanos


def _p_orb_dias(r):
    a = r.a_final_ua * UA
    motor = MotorMHD(r.nombre_planeta)
    G = 6.674e-11
    n = math.sqrt(G * (motor.M_estrella + motor.M) / a ** 3)
    return 2 * math.pi / n / 86400.0


# --- 1 y 2: migracion y rotacion independientes de dt ----------------------

@pytest.mark.parametrize("nombre", ["TRAPPIST_1e", "Proxima_b"])
def test_rotacion_sincronica_e_independiente_de_dt(nombre):
    if nombre not in PLANETAS:
        pytest.skip(f"{nombre} no esta en la base")
    periodos = []
    for dt in (5_000, 50_000):
        r = simular_planeta(nombre, t_max_gyr=T_GYR, dt_yr=dt, incluir_serie=False)
        assert r.error is None
        periodos.append(r.P_rot_final_dias)
    p_orb = _p_orb_dias(r)
    for p in periodos:
        # Prograda (no retrograda espuria) y cerca de la sincronia.
        assert p > 0, f"{nombre}: rotacion retrograda espuria P={p}"
        assert abs(p - p_orb) / p_orb < 0.25, f"{nombre}: P_rot={p:.2f} d vs P_orb={p_orb:.2f} d"
    assert abs(periodos[0] - periodos[1]) / p_orb < 0.10, f"{nombre}: depende de dt {periodos}"


@pytest.mark.parametrize("nombre", ["HD_209458b", "WASP_12b", "TRAPPIST_1e"])
def test_migracion_independiente_de_dt(nombre):
    if nombre not in PLANETAS:
        pytest.skip(f"{nombre} no esta en la base")
    a_fin = []
    for dt in (5_000, 50_000):
        r = simular_planeta(nombre, t_max_gyr=T_GYR, dt_yr=dt, incluir_serie=False)
        a_fin.append(r.a_final_ua)
    assert abs(a_fin[0] - a_fin[1]) / a_fin[0] < 0.01, f"{nombre}: a_final depende de dt {a_fin}"


def test_migracion_integracion_exacta_vs_pasos_cortos():
    m = MotorMHD("WASP_12b")
    m.a_colapso = 1e-9
    a0 = PLANETAS["WASP_12b"]["a_inicial"]
    año = 3.156e7
    a_largo, _ = m._evolucion_orbital_marea_estelar(a0, 1e6 * año, 0.0)
    a_corto = a0
    for _ in range(100):
        a_corto, _ = m._evolucion_orbital_marea_estelar(a_corto, 1e4 * año, 0.0)
    assert a_largo < a0
    assert abs(a_largo - a_corto) / a0 < 1e-9


def test_rotacion_sin_superrotacion():
    # Ningun planeta cercano debe terminar girando mas rapido que su
    # limite de ruptura (antes pasaba por la oscilacion de la marea).
    G = 6.674e-11
    for nombre in ["TRAPPIST_1e", "Proxima_b", "GJ_367b", "K2_141b"]:
        if nombre not in PLANETAS:
            continue
        r = simular_planeta(nombre, t_max_gyr=T_GYR, dt_yr=50_000, incluir_serie=False)
        m = MotorMHD(nombre)
        w_ruptura = math.sqrt(G * m.M / m.R_p ** 3)
        w = 2 * math.pi / (abs(r.P_rot_final_dias) * 86400.0)
        assert w < w_ruptura, f"{nombre}: w={w:.3e} > ruptura {w_ruptura:.3e}"


# --- 3: se_estrello con limite fisico --------------------------------------

# Antes, cualquier planeta con a < 0.01 UA salia "estrellado" desde t=0.
# GJ 367 b y K2-141 b si decaen fisicamente (K2-141 b en ~100 Myr con
# Q'*=1e7), asi que para ellos se prueba un intervalo corto (10 Myr);
# los de Kepler-444 (a > 0.04 UA) deben sobrevivir los 4.5 Gyr.
@pytest.mark.parametrize("nombre,t_gyr", [("GJ_367b", 0.01), ("K2_141b", 0.01),
                                          ("Kepler_444b", 4.5), ("Kepler_444f", 4.5)])
def test_no_se_estrella_planeta_ultracercano(nombre, t_gyr):
    if nombre not in PLANETAS:
        pytest.skip(f"{nombre} no esta en la base")
    r = simular_planeta(nombre, t_max_gyr=t_gyr, dt_yr=10_000, incluir_serie=False)
    assert r.error is None
    assert not r.se_estrello, f"{nombre} marcado como estrellado (a_final={r.a_final_ua:.5f} UA)"


def test_tierra_y_jupiter_no_migran():
    for nombre in ("Tierra", "Jupiter"):
        r = simular_planeta(nombre, t_max_gyr=4.5, dt_yr=100_000, incluir_serie=False)
        assert abs(r.a_final_ua - r.a_inicial_ua) / r.a_inicial_ua < 1e-6


# --- 4: XUV escala como a^-2 -----------------------------------------------

def test_xuv_escala_con_inverso_del_cuadrado():
    perdidas = {}
    for a_ua in (0.5, 1.0):
        atm = Atmosfera(M_atm_inicial=1e20, M_planeta=6e24, R_planeta=6.4e6,
                        F_XUV_inicial=0.005, distancia_ua=a_ua)
        m = atm.actualizar(t_gyr=0.005, dt=3.156e7, a_ua=a_ua)
        perdidas[a_ua] = 1e20 - m
    razon = perdidas[0.5] / perdidas[1.0]
    assert razon == pytest.approx(4.0, rel=1e-6), f"razon {razon} (a^-4 daria 16)"


# --- 5: torque atmosferico con atmosfera perdida ---------------------------

def test_torque_atm_cero_si_atmosfera_perdida():
    m = MotorMHD("Venus", parametros_extra={"modelo_atmosfera": True,
                                           "torque_atmosferico": True})
    assert m.torque_atmosferico_on

    class E:  # estado minimo
        M_atm = 0.0
        a = 0.723 * UA

    assert m.calcular_torque_atmosferico_termico(E(), -2.99e-7, 3.2e-7) == 0.0


# --- 6: oblicuidad ---------------------------------------------------------

def test_oblicuidad_jupiter_sin_penalizacion_y_urano_con():
    rj = simular_planeta("Jupiter", t_max_gyr=4.5, dt_yr=100_000, max_puntos_serie=100)
    ru = simular_planeta("Urano", t_max_gyr=4.5, dt_yr=100_000, max_puntos_serie=100)
    assert calcular_mhi(rj)["penalizacion_obl_pts"] == 0.0
    assert calcular_mhi(ru)["penalizacion_obl_pts"] < 0.0


# --- 7: datos corregidos ---------------------------------------------------

def _a_ua(p):
    return p["a_inicial"] / UA


@pytest.mark.parametrize("nombre,a_ua", [
    ("GJ_1132b", 0.01570), ("LHS_475b", 0.0204), ("GJ_3293b", 0.14339),
    ("HD_27894c", 0.198), ("HD_27894d", 5.448),
])
def test_datos_corregidos(nombre, a_ua):
    if nombre not in PLANETAS:
        pytest.skip(f"{nombre} no esta en la base")
    assert _a_ua(PLANETAS[nombre]) == pytest.approx(a_ua, rel=0.01)
