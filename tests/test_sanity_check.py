"""
Tests unitarios para sanity_check.py.
Valida que el sanity check funciona correctamente con datos reales y extremos.
"""
import pytest
from sanity_check import validar_coherencia, _densidad_g_cm3, _periodo_kepler_anios

M_TIERRA_KG = 5.972e24
R_TIERRA_M = 6.371e6
UA_M = 1.495978707e11
MSUN_KG = 1.98847e30


class TestDensidad:
    def test_tierra_tiene_densidad_correcta(self):
        # Densidad real de la Tierra: ~5.51 g/cm3
        densidad = _densidad_g_cm3(M_TIERRA_KG, R_TIERRA_M)
        assert densidad == pytest.approx(5.51, abs=0.05)

    def test_radio_mayor_da_densidad_menor(self):
        d1 = _densidad_g_cm3(M_TIERRA_KG, R_TIERRA_M)
        d2 = _densidad_g_cm3(M_TIERRA_KG, R_TIERRA_M * 2)
        assert d2 < d1

    def test_masa_cero_devuelve_densidad_cero(self):
        # Chequeo de la funcion interna en si misma (distinto del test
        # de validar_coherencia con M=0, que bloquea antes de llegar a
        # calcular densidad -- este prueba _densidad_g_cm3 aislada).
        assert _densidad_g_cm3(0.0, R_TIERRA_M) == 0.0


class TestPeriodoKepler:
    def test_tierra_da_un_anio(self):
        periodo = _periodo_kepler_anios(UA_M, MSUN_KG)
        assert periodo == pytest.approx(1.0, abs=0.01)

    def test_masa_estelar_cero_da_nan(self):
        periodo = _periodo_kepler_anios(UA_M, 0.0)
        assert periodo != periodo  # NaN no es igual a si mismo

    def test_masa_estelar_negativa_da_nan(self):
        periodo = _periodo_kepler_anios(UA_M, -MSUN_KG)
        assert periodo != periodo


class TestValidarCoherencia:
    def test_tierra_es_coherente_sin_advertencias(self):
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is True
        assert resultado["advertencias"] == []

    def test_masa_negativa_bloquea(self):
        datos = {"M": -1.0, "R_p": R_TIERRA_M, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is False

    def test_masa_cero_bloquea(self):
        datos = {"M": 0.0, "R_p": R_TIERRA_M, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is False

    def test_masa_ausente_bloquea(self):
        datos = {"R_p": R_TIERRA_M, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is False

    def test_radio_negativo_bloquea(self):
        datos = {"M": M_TIERRA_KG, "R_p": -1.0, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is False

    def test_semieje_negativo_bloquea(self):
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M, "a_inicial": -UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is False

    def test_semieje_ausente_no_bloquea(self):
        # a_inicial es opcional -- solo bloquea si esta presente Y es <= 0
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is True

    def test_densidad_muy_baja_da_advertencia_no_bloquea(self):
        # Radio enorme para una masa terrestre -> densidad absurdamente baja
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M * 20, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is True  # NO bloquea, es advertencia
        assert len(resultado["advertencias"]) == 1
        assert "Densidad muy baja" in resultado["advertencias"][0]

    def test_densidad_muy_alta_da_advertencia_no_bloquea(self):
        # Radio chiquito para una masa terrestre -> densidad absurdamente alta
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M / 10, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is True
        assert len(resultado["advertencias"]) == 1
        assert "Densidad muy alta" in resultado["advertencias"][0]

    def test_densidad_kepler51_no_dispara_advertencia(self):
        # Caso real citado en el propio comentario de sanity_check.py:
        # Kepler-51b/c/d miden ~0.1 g/cm3 -- el piso (0.05) tiene que
        # dejarlo pasar sin advertencia, es la razon de que exista ese piso.
        # Masa ~2 masas terrestres, radio grande (gigante "algodon de azucar")
        masa = 2 * M_TIERRA_KG
        # Despejar radio para dar ~0.1 g/cm3 de densidad
        import math
        densidad_objetivo_kg_m3 = 0.1 * 1000
        radio = (masa / densidad_objetivo_kg_m3 / (4/3 * math.pi)) ** (1/3)
        datos = {"M": masa, "R_p": radio, "a_inicial": UA_M}
        resultado = validar_coherencia(datos)
        assert resultado["coherente"] is True
        assert resultado["advertencias"] == []

    def test_kepler_coherente_no_da_advertencia(self):
        # Periodo real de la Tierra (~365.25 dias) a 1 UA de una estrella
        # solar -- debe coincidir con Kepler sin advertencia.
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M, "a_inicial": UA_M,
                 "periodo_dias": 365.25}
        resultado = validar_coherencia(datos, masa_estrella_kg=MSUN_KG)
        assert resultado["coherente"] is True
        assert resultado["advertencias"] == []

    def test_kepler_incoherente_da_advertencia(self):
        # Periodo absurdamente corto para a=1 UA alrededor del Sol
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M, "a_inicial": UA_M,
                 "periodo_dias": 5.0}
        resultado = validar_coherencia(datos, masa_estrella_kg=MSUN_KG)
        assert resultado["coherente"] is True  # sigue sin bloquear
        assert any("Kepler" in a for a in resultado["advertencias"])

    def test_sin_masa_estrella_no_chequea_kepler(self):
        # Sin masa_estrella_kg, el chequeo de Kepler ni se intenta,
        # aunque el periodo sea absurdo.
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M, "a_inicial": UA_M,
                 "periodo_dias": 5.0}
        resultado = validar_coherencia(datos)  # sin masa_estrella_kg
        assert resultado["advertencias"] == []

    def test_no_modifica_el_dict_de_entrada(self):
        datos = {"M": M_TIERRA_KG, "R_p": R_TIERRA_M, "a_inicial": UA_M}
        copia = dict(datos)
        validar_coherencia(datos)
        assert datos == copia
