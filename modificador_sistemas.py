"""
modificador_sistemas.py
MHD-INT v5.9 (módulo de extensión, BETA)

Toma un planeta existente de la base de datos, lo modifica (órbita, masa,
campo magnético, agregar luna), simula la versión modificada con el motor
ya existente (sin tocar engine.py), y la compara contra el original.

ALCANCE (auditoría 2026-08-09) — LEER ANTES DE USAR:
La propuesta original de este módulo incluía experimentos de dinámica de
sistema completo ("¿qué pasa si Júpiter no existiera?", "¿puede un
Júpiter caliente expulsar a la Tierra?"). Se verificó contra engine.py
(MotorMHD.simular) que el motor simula CADA planeta de forma
independiente: estrella-planeta(-luna), sin ningún acoplamiento
gravitacional planeta-planeta. Quitar o agregar un planeta en la lista
NO cambia en nada la física simulada de los demás -- no hay resonancias,
perturbaciones orbitales, ni riesgo de eyección que este motor pueda
calcular. Ofrecer esos dos experimentos habría sido presentar un
resultado sin respaldo físico (ver MODULO_QUITAR_JUPITER_NO_IMPLEMENTADO
abajo, que documenta explícitamente por qué se excluyó en vez de
callarlo).

LO QUE SÍ HACE ESTE MÓDULO (física estrella-planeta-luna real, ya
validada en el resto de MHD-INT, solo con condiciones iniciales
distintas -- no es física nueva):
  - Mover un planeta a otra órbita (a_inicial)
  - Cambiar la masa de un planeta
  - Cambiar el campo magnético inicial de un planeta
  - Agregar/modificar una luna (ya soportado por
    MotorMHD.lunas_personalizadas, generalizado aquí a planetas
    arbitrarios en vez de solo Tierra)
  - Comparar el resultado modificado contra el original (ΔB, ΔMHI,
    ΔP_rot, Δa, campo_protegido antes/después)

NO TOCA engine.py — todas las modificaciones se hacen sobre una COPIA del
diccionario de parámetros del planeta, pasada a simular_planeta() vía sus
parámetros ya existentes (planetas=, lunas_personalizadas=), que ya
soportan exactamente este caso de uso.
"""

import copy

from engine import simular_planeta
from database import PLANETAS, LUNAS
from habitabilidad import calcular_mhi

UA = 1.495978707e11


class ModificadorSistemas:
    """
    Toma un planeta base de PLANETAS, permite modificarlo, y compara la
    simulación modificada contra la simulación del planeta original.

    Uso:
        m = ModificadorSistemas("Tierra")
        m.cambiar_masa(10.0)          # 10 M_tierra
        m.mover_planeta(1.5)          # 1.5 UA
        resultado = m.simular_y_comparar()
    """

    def __init__(self, nombre_planeta_base):
        if nombre_planeta_base not in PLANETAS:
            raise ValueError(f"'{nombre_planeta_base}' no existe en la base de datos.")
        self.nombre_base = nombre_planeta_base
        self.datos_originales = copy.deepcopy(PLANETAS[nombre_planeta_base])
        self.datos_modificados = copy.deepcopy(PLANETAS[nombre_planeta_base])
        self.luna_personalizada = None
        self.modificaciones_aplicadas = []

    # ------------------------------------------------------------------
    # Modificaciones individuales
    # ------------------------------------------------------------------
    def mover_planeta(self, a_ua):
        """Cambia el semieje orbital inicial, en UA."""
        self.datos_modificados["a_inicial"] = a_ua * UA
        self.modificaciones_aplicadas.append(f"órbita → {a_ua} UA")
        return self

    def cambiar_masa(self, M_tierra):
        """Cambia la masa del planeta, en masas terrestres."""
        M_TIERRA = 5.972e24
        self.datos_modificados["M"] = M_tierra * M_TIERRA
        self.modificaciones_aplicadas.append(f"masa → {M_tierra} M⊕")
        return self

    def cambiar_campo_magnetico(self, B_gauss):
        """Cambia el campo magnético inicial, en Gauss."""
        self.datos_modificados["B_p_inicial"] = B_gauss * 1.0e-4  # Gauss -> Tesla
        self.modificaciones_aplicadas.append(f"B inicial → {B_gauss} G")
        return self

    def agregar_luna(self, masa_luna_kg, a_luna_inicial_ua, k2=0.3, Q_p=12):
        """Agrega (o reemplaza) una luna al planeta modificado. Antes solo
        la Tierra tenía entrada en LUNAS -- MotorMHD ya soporta
        lunas_personalizadas, así que esto es generalización de uso, no
        física nueva."""
        self.luna_personalizada = {
            self.nombre_base: {
                "masa": masa_luna_kg,
                "a_luna_inicial": a_luna_inicial_ua * UA,
                "k2": k2, "Q_p": Q_p,
            }
        }
        self.modificaciones_aplicadas.append(
            f"luna agregada (a_inicial={a_luna_inicial_ua} UA)"
        )
        return self

    # ------------------------------------------------------------------
    # Escenarios predefinidos (solo los que el motor puede responder)
    # ------------------------------------------------------------------
    def escenario_super_tierra(self):
        """'Hacer Tierra gigante' generalizado: sube la masa a 10 M⊕."""
        return self.cambiar_masa(10.0)

    def escenario_planeta_a_zona_habitable(self, a_ua=1.0):
        """Generalización de 'mover Marte a la zona habitable'."""
        return self.mover_planeta(a_ua)

    @staticmethod
    def experimentos_no_implementados():
        """Devuelve la lista de experimentos de la propuesta original que
        NO se implementaron, con la razón -- para que quede visible en la
        UI en vez de simplemente omitidos."""
        return [
            {
                "experimento": "Quitar Júpiter del Sistema Solar",
                "razon": "Requiere interacción gravitacional planeta-planeta "
                          "(resonancias, protección del cinturón de asteroides). "
                          "El motor simula cada planeta de forma independiente "
                          "(estrella-planeta-luna); quitar Júpiter de la lista "
                          "no altera en nada la física simulada de la Tierra.",
            },
            {
                "experimento": "Añadir un Júpiter caliente y ver si expulsa la Tierra",
                "razon": "Mismo motivo: eyección orbital y barrido de resonancias "
                          "son fenómenos de N-cuerpos. Este motor no los modela.",
            },
        ]

    # ------------------------------------------------------------------
    # Simulación y comparación
    # ------------------------------------------------------------------
    def simular_y_comparar(self, t_max_gyr=5.0, dt_yr=1000.0):
        """Simula el planeta original y el modificado, devuelve ambos
        resultados + un diccionario de diferencias (Delta).

        FIX (revisión previa a integrar a v5.2): el planeta modificado se
        simula bajo la clave "{nombre}_modificado" -- que nunca existe en
        LUNAS. Si el planeta base SÍ tenía luna real (hoy, solo "Tierra")
        y el usuario no llamó a agregar_luna(), la búsqueda por nombre en
        el motor (self.lunas_db.get(nombre_planeta)) no la encontraba, y
        la comparación terminaba siendo "original CON luna" vs "modificado
        SIN luna" sin que nada lo avisara -- un cambio no pedido colándose
        en el delta. Se traslada automáticamente la luna original a la
        clave del modificado, salvo que el usuario ya haya llamado a
        agregar_luna() (en cuyo caso se respeta lo que pidió a propósito).
        """
        nombre_mod = f"{self.nombre_base}_modificado"

        luna_original = LUNAS.get(self.nombre_base)
        if self.luna_personalizada is not None:
            lunas_para_modificado = {nombre_mod: self.luna_personalizada[self.nombre_base]}
            self.modificaciones_aplicadas.append(
                "luna: usando la personalizada indicada con agregar_luna()"
            )
        elif luna_original is not None:
            lunas_para_modificado = {nombre_mod: dict(luna_original)}
            self.modificaciones_aplicadas.append(
                f"luna: se conserva la luna original de {self.nombre_base} "
                "(no se pidió cambiarla)"
            )
        else:
            lunas_para_modificado = None

        r_original = simular_planeta(
            self.nombre_base, t_max_gyr=t_max_gyr, dt_yr=dt_yr,
            planetas={self.nombre_base: self.datos_originales},
        )
        r_modificado = simular_planeta(
            nombre_mod, t_max_gyr=t_max_gyr, dt_yr=dt_yr,
            planetas={nombre_mod: self.datos_modificados},
            lunas_personalizadas=lunas_para_modificado,
        )

        if not r_original.es_valido() or not r_modificado.es_valido():
            return {
                "original": r_original, "modificado": r_modificado,
                "error": r_original.error or r_modificado.error,
                "modificaciones": self.modificaciones_aplicadas,
            }

        # Chequeo defensivo de estabilidad numérica (mismo criterio que se
        # agregó a la luna personalizada del modo Sintético en
        # app_streamlit_pro.py). Este módulo permite valores libres de
        # masa/distancia/campo/luna sobre CUALQUIERA de los 300 planetas
        # sin el rango acotado de un slider -- el mismo integrador de paso
        # fijo que puede divergir ahí puede divergir acá. No hay UI propia
        # todavía para modificador_sistemas.py, pero se deja la advertencia
        # ya calculada en el resultado para que cualquier UI futura no
        # tenga que redescubrir el problema.
        advertencia_estabilidad = None
        if abs(getattr(r_modificado, "w_final", 0.0)) > 1e-2:
            advertencia_estabilidad = (
                "El planeta modificado dio una rotación final físicamente "
                "imposible (integrador de paso fijo divergiendo). El "
                "resultado no es confiable -- probá con una modificación "
                "menos extrema."
            )

        mhi_original = calcular_mhi(r_original)
        mhi_modificado = calcular_mhi(r_modificado)

        delta = {
            "delta_B_gauss": r_modificado.B_final_gauss - r_original.B_final_gauss,
            "delta_MHI": mhi_modificado["mhi_total"] - mhi_original["mhi_total"],
            "delta_P_rot_dias": r_modificado.P_rot_final_dias - r_original.P_rot_final_dias,
            "delta_a_ua": r_modificado.a_final_ua - r_original.a_final_ua,
            "campo_protegido_original": r_original.campo_protegido,
            "campo_protegido_modificado": r_modificado.campo_protegido,
            "se_estrello_modificado": r_modificado.se_estrello,
        }

        return {
            "original": r_original, "modificado": r_modificado,
            "mhi_original": mhi_original, "mhi_modificado": mhi_modificado,
            "delta": delta, "modificaciones": self.modificaciones_aplicadas,
            "advertencia_estabilidad": advertencia_estabilidad,
            "error": None,
        }
