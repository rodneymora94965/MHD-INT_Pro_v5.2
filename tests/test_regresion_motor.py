"""
Tests de regresión para el motor físico.
Valida que los cuerpos calibrados en validacion.py (DATOS_REALES) siguen
dando resultados dentro de las tolerancias documentadas.

IMPORTANTE: estos tests corren el motor real (con Numba si está
disponible), así que tardan varios segundos cada uno. No los corras en
cada cambio chico, solo antes de releases y cuando toques
engine.py/termica.py/atmosfera.py.

NOTA: se parametrizan directamente sobre validacion.DATOS_REALES (hoy
son 6 cuerpos: Tierra, Venus, Marte, Jupiter, Urano, Neptuno) en vez de
hardcodear una lista acá -- si se agrega o saca un cuerpo de esa lista,
este archivo lo sigue automáticamente sin tener que tocarlo.

Para correr solo estos tests:
    pytest tests/test_regresion_motor.py -v
"""
import pytest
from validacion import validar_planeta, DATOS_REALES, TOLERANCIA_DEFECTO


@pytest.mark.parametrize("nombre", list(DATOS_REALES.keys()))
def test_cuerpo_calibrado_aprueba(nombre):
    resultado = validar_planeta(nombre, tolerancia=TOLERANCIA_DEFECTO)
    detalle = "; ".join(
        f"{clave}: sim={m['simulado']} real={m['real']} error={m['error_relativo_pct']}%"
        for clave, m in resultado["metricas"].items()
        if not m["aprueba"]
    )
    assert resultado["aprueba"], (
        f"{nombre} no aprobó la validación con tolerancia "
        f"{TOLERANCIA_DEFECTO*100:.0f}%. Métricas fuera de rango: {detalle or resultado['error_simulacion']}"
    )


def test_tierra_no_se_estrella():
    # Chequeo puntual además del genérico de arriba -- la Tierra es el
    # caso más usado en demos/capturas de pantalla, si esto se rompe
    # es grave y visible enseguida.
    resultado = validar_planeta("Tierra")
    assert resultado["error_simulacion"] is None


def test_jupiter_campo_magnetico_en_rango():
    # Jupiter es el unico de los 6 con B_gauss de referencia distinto
    # de None -- vale la pena un chequeo directo sobre esa metrica en
    # particular, no solo el agregado "aprueba" de todas juntas.
    resultado = validar_planeta("Jupiter")
    assert "B_gauss" in resultado["metricas"]
    assert resultado["metricas"]["B_gauss"]["aprueba"] is True


def test_urano_es_retrogrado():
    # Urano es el unico de los 6 marcado como retrogrado=True en
    # DATOS_REALES -- si el motor alguna vez cambia el signo de w_final
    # sin querer, este test lo detecta puntualmente.
    resultado = validar_planeta("Urano")
    assert "sentido_rotacion" in resultado["metricas"]
    assert resultado["metricas"]["sentido_rotacion"]["aprueba"] is True


def test_cuerpo_sin_datos_de_referencia_lanza_keyerror():
    with pytest.raises(KeyError):
        validar_planeta("PlanetaQueNoExiste")


# ---------------------------------------------------------------------
# Tests nombrados por cuerpo/métrica -- complementan (no reemplazan) el
# parametrizado de arriba. El parametrizado te dice RÁPIDO si algo se
# rompió en cualquiera de los 6 cuerpos; estos te dicen, sin abrir el
# diccionario de métricas, CUÁL valor físico puntual se salió de rango
# con solo mirar el nombre del test que falló. Los rangos usan el mismo
# 5% de tolerancia que TOLERANCIA_DEFECTO en validacion.py, calculado
# sobre los valores reales de DATOS_REALES -- si alguno de los dos
# cambia, hay que revisar el otro para que no queden desincronizados.
# ---------------------------------------------------------------------
from engine import simular_planeta
from habitabilidad import calcular_mhi


class TestTierra:
    def test_campo_magnetico(self):
        r = simular_planeta("Tierra", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 0.25 < r.B_final_gauss < 0.40

    def test_distancia_orbital(self):
        r = simular_planeta("Tierra", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 0.95 < r.a_final_ua < 1.05

    def test_excentricidad(self):
        r = simular_planeta("Tierra", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 0.01 < r.e_final < 0.03

    def test_mhi_alto(self):
        r = simular_planeta("Tierra", t_max_gyr=4.5, dt_yr=50000, incluir_serie=True)
        assert r.es_valido() and r.tiene_serie()
        mhi = calcular_mhi(r)
        assert mhi["mhi_total"] > 70


class TestMarte:
    def test_campo_magnetico_bajo(self):
        r = simular_planeta("Marte", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert r.B_final_gauss < 0.01

    def test_distancia_orbital(self):
        r = simular_planeta("Marte", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 1.4 < r.a_final_ua < 1.6

    def test_excentricidad(self):
        r = simular_planeta("Marte", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 0.08 < r.e_final < 0.11


class TestJupiter:
    def test_campo_magnetico_fuerte(self):
        r = simular_planeta("Jupiter", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 3.5 < r.B_final_gauss < 5.0

    def test_distancia_orbital(self):
        r = simular_planeta("Jupiter", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 4.8 < r.a_final_ua < 5.5

    def test_rotacion_rapida(self):
        r = simular_planeta("Jupiter", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 0.35 < r.P_rot_final_dias < 0.50


class TestVenus:
    def test_campo_magnetico_bajo(self):
        r = simular_planeta("Venus", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert r.B_final_gauss < 0.01

    def test_distancia_orbital(self):
        r = simular_planeta("Venus", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert 0.68 < r.a_final_ua < 0.76

    def test_excentricidad_muy_baja(self):
        r = simular_planeta("Venus", t_max_gyr=4.5, dt_yr=50000, incluir_serie=False)
        assert r.es_valido()
        assert r.e_final < 0.02


class TestConsistencia:
    def test_simulacion_con_serie_sin_serie_da_mismo_resultado_final(self):
        """incluir_serie=True/False no debe afectar los valores finales
        -- solo controla si se guarda la serie temporal completa o no."""
        r_sin = simular_planeta("Tierra", t_max_gyr=1.0, dt_yr=50000, incluir_serie=False)
        r_con = simular_planeta("Tierra", t_max_gyr=1.0, dt_yr=50000, incluir_serie=True)

        assert r_sin.es_valido() and r_con.es_valido()
        assert abs(r_sin.B_final_gauss - r_con.B_final_gauss) < 1e-10
        assert abs(r_sin.a_final_ua - r_con.a_final_ua) < 1e-10
        assert abs(r_sin.e_final - r_con.e_final) < 1e-10
