"""
database_estrellas.py
MHD-INT v5.9 — Catálogo de estrellas T Tauri (Fase 2, módulo de disco
protoplanetario)

ESQUEMA (auditoría 2026-08-09): reescrito para reflejar los parámetros
que la Ecuación 23 de Lai, Foucart & Lin (2011) realmente usa — ver
disco_protoplanetario.py. Cambios respecto al esquema original propuesto:

  - "R_disco" y "tau_disco" (radio/vida del disco a gran escala) SE
    ELIMINAN como campos de entrada al motor de oblicuidad. La versión
    anterior los usaba como radio de acoplamiento; la física real usa
    r_in (radio de truncamiento magnetosférico), que es ~10-50x más
    pequeño y se DERIVA de B/M★/Ṁ, no se elige a mano. tau_disco se
    conserva solo como referencia informativa (vida útil del disco
    observado), no entra en el cálculo de r_in.
  - Se agrega R_estrella_rsol como campo directo (antes se derivaba de
    una relación masa-radio genérica; para estrellas catalogadas
    individualmente, usar el radio real medido/estimado es mejor dato).
  - "oblicuidad_medida" se renombra "oblicuidad_referencia" con un campo
    adicional "tipo_referencia" — porque, salvo TW Hya, ninguna estrella
    de este catálogo tiene una medición directa de β (el ángulo que la
    Ec. 23 predice). Ver advertencia en cada entrada.
  - lambda_sugerido / zeta_tilde_sugerido: NO son parte del catálogo de
    la estrella (son propiedades del mecanismo físico, no de la
    estrella) — se dejan como constante global en
    disco_protoplanetario.py (LAMBDA_RANGO_SUGERIDO / 
    ZETA_TILDE_RANGO_SUGERIDO), no se repiten aquí por estrella.

TEXTO DE VENTA CORREGIDO (auditoría 2026-08-09): la propuesta original
de Fase 2 proponía "Validado contra DO Tau y TW Hya" con un semáforo
✅/⚠️ en la UI comparando predicción vs. dato medido. Eso sobre-promete:
- Solo r_in (el radio de truncamiento) está validado contra DO Tau, no
  la evolución de β completa.
- El dato de TW Hya NO es una medición directa de β — es una
  comparación indirecta entre inclinación de disco (5.8°, Teague et al.
  2019) e inclinación de spin estelar (~10°, Donati et al. 2024), con
  incertidumbre considerable, MEZCLADA con una tercera cantidad distinta
  (oblicuidad magnética dipolo-spin, también ~10°, Donati et al. 2011 —
  ver docstring de la entrada TW_Hya abajo).
Texto de venta reemplazado: "Calibrado con parámetros reales de 14
estrellas T Tauri documentadas en la literatura" — preciso, sigue siendo
un argumento de venta fuerte.
"""

M_SOL_KG = 1.98847e30

# ============================================================================
# CATÁLOGO — 14 estrellas T Tauri con parámetros reales de la literatura
# (M★, R★, B★, P_rot, Ṁ0 son datos observacionales; tau_disco es la vida
# útil del disco observada/estimada, informativa, no entra en el cálculo
# de r_in; oblicuidad_referencia es NO NULA solo para TW Hya, y con la
# advertencia de que no es una medición directa de β)
# ============================================================================
ESTRELLAS_T_TAURI = {
    "DO_Tau": {
        "nombre_display": "DO Tau",
        "M_estrella_msol": 0.60, "R_estrella_rsol": 2.0,
        "B_estrella_gauss": 500, "P_rot_dias": 5.0,
        "Mdot0_msol_yr": 2e-8, "tau_disco_myr_ref": 5.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica",
        "descripcion": "Referencia de validación del radio de truncamiento "
                        "(r_in) — ver validar_radio_truncamiento_contra_do_tau() "
                        "en disco_protoplanetario.py.",
        "fuente": "Bessolaz et al. 2008 (arXiv:0803.0577)",
    },
    "TW_Hya": {
        "nombre_display": "TW Hya",
        "M_estrella_msol": 0.80, "R_estrella_rsol": 1.16,
        "B_estrella_gauss": 1000, "P_rot_dias": 3.6,
        "Mdot0_msol_yr": 1e-8, "tau_disco_myr_ref": 8.0,
        "oblicuidad_referencia_deg": "5.8-10 (ver advertencia)",
        "tipo_referencia": "INDIRECTO — NO es beta medido. Mezcla 3 cantidades "
                            "distintas: inclinación del disco a la línea de "
                            "visión = 5.8°(+4.0/-1.7) (Teague et al. 2019, ALMA); "
                            "inclinación del eje de spin estelar a la línea de "
                            "visión ≈10° (Donati et al. 2024, SPIRou), descrita "
                            "por los autores como 'consistente con' la del disco, "
                            "no idéntica; oblicuidad magnética (ángulo eje de "
                            "rotación-eje del dipolo, una cantidad DISTINTA de "
                            "beta) ≈10° (Donati et al. 2011). Interpretación más "
                            "honesta: beta es probablemente pequeño para TW Hya, "
                            "pero no hay un número preciso de beta publicado.",
        "tipo_espectral": "T Tauri clásica",
        "descripcion": "Estrella más estudiada del catálogo (SPIRou 2019-2025). "
                        "Disco visto casi de frente.",
        "fuente": "Donati et al. 2011, Teague et al. 2019, Donati et al. 2024 "
                   "(arXiv:2405.04461)",
    },
    "HL_Tau": {
        "nombre_display": "HL Tau",
        "M_estrella_msol": 0.65, "R_estrella_rsol": 2.1,
        "B_estrella_gauss": 800, "P_rot_dias": 6.0,
        "Mdot0_msol_yr": 3e-8, "tau_disco_myr_ref": 4.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica",
        "descripcion": "Famosa por los anillos concéntricos de su disco "
                        "(primera imagen ALMA de alta resolución, 2014).",
        "fuente": "ALMA Partnership et al. 2015",
    },
    "BP_Tau": {
        "nombre_display": "BP Tau",
        "M_estrella_msol": 0.80, "R_estrella_rsol": 1.8,
        "B_estrella_gauss": 1200, "P_rot_dias": 3.5,
        "Mdot0_msol_yr": 2e-8, "tau_disco_myr_ref": 3.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica",
        "descripcion": "Uno de los primeros T Tauri con mapeo Zeeman-Doppler "
                        "del campo magnético superficial.",
        "fuente": "Johns-Krull et al. 2000",
    },
    "FU_Ori": {
        "nombre_display": "FU Ori",
        "M_estrella_msol": 0.80, "R_estrella_rsol": 2.5,
        "B_estrella_gauss": 300, "P_rot_dias": 8.0,
        "Mdot0_msol_yr": 5e-8, "tau_disco_myr_ref": 2.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "FUor (estallido de acreción)",
        "descripcion": "Prototipo de estallido FUor — episodio de acreción muy "
                        "por encima del Ṁ típico T Tauri. Ṁ0 aquí es una "
                        "instantánea, no representativa de toda su vida.",
        "fuente": "Kenyon et al. 1993",
    },
    "V347_Aur": {
        "nombre_display": "V347 Aurigae",
        "M_estrella_msol": 0.70, "R_estrella_rsol": 2.2,
        "B_estrella_gauss": 600, "P_rot_dias": 7.0,
        "Mdot0_msol_yr": 2.5e-8, "tau_disco_myr_ref": 5.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica",
        "descripcion": "T Tauri clásica de la región de Auriga.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
    "CoKu_Tau_4": {
        "nombre_display": "CoKu Tau/4",
        "M_estrella_msol": 0.70, "R_estrella_rsol": 2.0,
        "B_estrella_gauss": 400, "P_rot_dias": 6.0,
        "Mdot0_msol_yr": 1e-8, "tau_disco_myr_ref": 4.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri con cavidad interna (transicional)",
        "descripcion": "Disco de transición con cavidad central — posible "
                        "sistema binario compacto o planeta en formación.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
    "GQ_Lup": {
        "nombre_display": "GQ Lupi",
        "M_estrella_msol": 0.70, "R_estrella_rsol": 2.5,
        "B_estrella_gauss": 200, "P_rot_dias": 8.0,
        "Mdot0_msol_yr": 1.5e-8, "tau_disco_myr_ref": 5.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica",
        "descripcion": "Conocida por su compañero de masa planetaria/enana "
                        "marrón (GQ Lupi b) en órbita ancha.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
    "AA_Tau": {
        "nombre_display": "AA Tau",
        "M_estrella_msol": 0.80, "R_estrella_rsol": 1.5,
        "B_estrella_gauss": 800, "P_rot_dias": 3.0,
        "Mdot0_msol_yr": 2e-8, "tau_disco_myr_ref": 3.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica (dipper)",
        "descripcion": "Prototipo de estrella 'dipper' — eclipses periódicos "
                        "por material del disco interno alzado por el campo "
                        "magnético, evidencia observacional directa de "
                        "truncamiento magnetosférico no-alineado.",
        "fuente": "Bouvier et al. 1999",
    },
    "T_Tau": {
        "nombre_display": "T Tauri (la estrella prototipo)",
        "M_estrella_msol": 1.00, "R_estrella_rsol": 2.0,
        "B_estrella_gauss": 300, "P_rot_dias": 6.0,
        "Mdot0_msol_yr": 1e-8, "tau_disco_myr_ref": 4.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri (prototipo de la clase)",
        "descripcion": "La estrella que da nombre a toda la clase T Tauri.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
    "DG_Tau": {
        "nombre_display": "DG Tau",
        "M_estrella_msol": 0.70, "R_estrella_rsol": 2.0,
        "B_estrella_gauss": 400, "P_rot_dias": 5.0,
        "Mdot0_msol_yr": 2e-8, "tau_disco_myr_ref": 3.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica con jet",
        "descripcion": "Fuente prominente de jet óptico colimado.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
    "RW_Aur": {
        "nombre_display": "RW Aurigae",
        "M_estrella_msol": 0.80, "R_estrella_rsol": 2.0,
        "B_estrella_gauss": 500, "P_rot_dias": 4.0,
        "Mdot0_msol_yr": 3e-8, "tau_disco_myr_ref": 3.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri en sistema binario",
        "descripcion": "Sistema binario T Tauri con interacción de marea "
                        "documentada entre discos.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
    "RU_Lup": {
        "nombre_display": "RU Lupi",
        "M_estrella_msol": 0.70, "R_estrella_rsol": 2.0,
        "B_estrella_gauss": 300, "P_rot_dias": 6.0,
        "Mdot0_msol_yr": 1e-8, "tau_disco_myr_ref": 4.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "T Tauri clásica, variabilidad fuerte",
        "descripcion": "T Tauri de acreción muy variable.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
    "EX_Lup": {
        "nombre_display": "EX Lupi",
        "M_estrella_msol": 0.70, "R_estrella_rsol": 2.0,
        "B_estrella_gauss": 400, "P_rot_dias": 5.0,
        "Mdot0_msol_yr": 2e-8, "tau_disco_myr_ref": 3.0,
        "oblicuidad_referencia_deg": None, "tipo_referencia": None,
        "tipo_espectral": "EXor (estallido de acreción)",
        "descripcion": "Prototipo de estallido EXor (más corto/frecuente que "
                        "un FUor). Ṁ0 aquí es una instantánea.",
        "fuente": "Sin fuente individual confirmada — parámetros de catálogo general",
    },
}


def listar_estrellas():
    """Devuelve la lista de claves del catálogo, para poblar un selector."""
    return list(ESTRELLAS_T_TAURI.keys())


def obtener_estrella(clave):
    """Devuelve el dict completo de una estrella del catálogo."""
    return ESTRELLAS_T_TAURI[clave]
