import numpy as np

# ============================================================================
# CORRECCIÓN v4.1 (auditoría 2026-07-22):
# (1) 23 de 47 planetas tenían w_estrella con el exponente del signo
#     invertido (ej. 2.9e6 en vez de 2.9e-6), lo cual invierte el signo del
#     torque magnético en calcular_torque_magnetico_numba(). Afectaba a los
#     8 planetas del Sistema Solar + 15 exoplanetas.
# (2) 36 de 47 planetas tenían B_p_inicial con el mismo bug de exponente
#     invertido (ej. 3.1e5 T en vez de 3.1e-5 T para la Tierra). Confirmado
#     por validar_todos(): tras corregir, B_inicial de Tierra y Júpiter
#     coinciden exactamente con los valores reales en validacion.py
#     (0.31 G y 4.2 G respectivamente).
# ============================================================================

ESTRELLAS = {
    "Sol": {"tipo_espectral": "G2V", "masa": 1.0 * 1.98847e30},
    "Próxima_Centauri": {"tipo_espectral": "M5.5V", "masa": 0.12 * 1.98847e30},
    "GJ_1132": {"tipo_espectral": "M3.5V", "masa": 0.18 * 1.98847e30},
    "WASP_12": {"tipo_espectral": "F8V", "masa": 1.35 * 1.98847e30},
    "TRAPPIST_1": {"tipo_espectral": "M8V", "masa": 0.089 * 1.98847e30},
    "Kepler_442": {"tipo_espectral": "K5V", "masa": 0.61 * 1.98847e30},
    "Kepler_452": {"tipo_espectral": "G2V", "masa": 1.04 * 1.98847e30},
    "GJ_581": {"tipo_espectral": "M3V", "masa": 0.31 * 1.98847e30},
    "HD_209458": {"tipo_espectral": "F8V", "masa": 1.20 * 1.98847e30},
    "HD_189733": {"tipo_espectral": "K1V", "masa": 0.80 * 1.98847e30},
    "Barnard": {"tipo_espectral": "M4V", "masa": 0.16 * 1.98847e30},
    "GJ_273": {"tipo_espectral": "M3.5V", "masa": 0.29 * 1.98847e30},
    "Teegarden": {"tipo_espectral": "M7V", "masa": 0.089 * 1.98847e30},
    "Luyten": {"tipo_espectral": "M3.5V", "masa": 0.29 * 1.98847e30},
    "Wolf_1061": {"tipo_espectral": "M3V", "masa": 0.25 * 1.98847e30},
    "Gliese_667": {"tipo_espectral": "M2V", "masa": 0.33 * 1.98847e30},
    "Gliese_832": {"tipo_espectral": "M1.5V", "masa": 0.45 * 1.98847e30},
    "Kepler_186": {"tipo_espectral": "M1V", "masa": 0.48 * 1.98847e30},
    "Kepler_62": {"tipo_espectral": "K2V", "masa": 0.69 * 1.98847e30},
    "Kepler_69": {"tipo_espectral": "G4V", "masa": 0.81 * 1.98847e30},
    "Kepler_22": {"tipo_espectral": "G5V", "masa": 0.97 * 1.98847e30},
    "Kepler_1649": {"tipo_espectral": "M5V", "masa": 0.20 * 1.98847e30},
    "TOI_700": {"tipo_espectral": "M2V", "masa": 0.41 * 1.98847e30},
    "Tau_Ceti": {"tipo_espectral": "G8V", "masa": 0.78 * 1.98847e30},
    "GJ_180": {"tipo_espectral": "M2V", "masa": 0.39 * 1.98847e30},
    "GJ_422": {"tipo_espectral": "M2V", "masa": 0.40 * 1.98847e30},
    "K2_18": {"tipo_espectral": "M2.5V", "masa": 0.36 * 1.98847e30},
    "HD_40307": {"tipo_espectral": "K2.5V", "masa": 0.75 * 1.98847e30},
    "HD_85512": {"tipo_espectral": "K5V", "masa": 0.69 * 1.98847e30},
    "GJ_1214": {"tipo_espectral": "M4.5V", "masa": 0.15 * 1.98847e30},
    "55_Cancri": {"tipo_espectral": "G8V", "masa": 0.90 * 1.98847e30},
    "WASP_17": {"tipo_espectral": "F6V", "masa": 1.20 * 1.98847e30},
    "WASP_39": {"tipo_espectral": "G8V", "masa": 0.93 * 1.98847e30},
    "CoRoT_7": {"tipo_espectral": "G9V", "masa": 0.91 * 1.98847e30},
    "EPIC_201912552": {"tipo_espectral": "G5V", "masa": 0.95 * 1.98847e30},
    "K2_3": {"tipo_espectral": "M0V", "masa": 0.55 * 1.98847e30},
    "HD_219134": {"tipo_espectral": "K3V", "masa": 0.78 * 1.98847e30},
    "GJ_3293": {"tipo_espectral": "M2.5V", "masa": 0.40 * 1.98847e30},
    # --- Lote 1 (v5.4, exoplanetas TESS 2025-2026) ---
    # Masas estelares por tipo espectral = misma convención ya usada arriba
    # (aproximación por tipo, no medición individual), excepto donde se cita
    # un valor directo del paper. "Barnard" ya existe arriba (0.16 Msun) y se
    # reutiliza para Barnard_c en vez de duplicar.
    "TOI_4616": {"tipo_espectral": "M4V", "masa": 0.20 * 1.98847e30},
    "TOI_2431": {"tipo_espectral": "K5V", "masa": 0.75 * 1.98847e30},
    "TOI_1243_host": {"tipo_espectral": "M3V", "masa": 0.35 * 1.98847e30},
    "TOI_3862": {"tipo_espectral": "G8V", "masa": 0.87 * 1.98847e30},
    "TOI_3785": {"tipo_espectral": "M2V", "masa": 0.40 * 1.98847e30},
    "TOI_3568": {"tipo_espectral": "K2V", "masa": 0.75 * 1.98847e30},
    "TOI_4495": {"tipo_espectral": "F6V", "masa": 1.30 * 1.98847e30},
    "TOI_654": {"tipo_espectral": "M4V", "masa": 0.30 * 1.98847e30},
    # --- Lote 2 (v5.5, exoplanetas variados 2022-2026) ---
    "GJ_523": {"tipo_espectral": "K5V", "masa": 0.781 * 1.98847e30},
    "GJ_887": {"tipo_espectral": "M2V", "masa": 0.495 * 1.98847e30},
    "GJ_1137": {"tipo_espectral": "K2V", "masa": 0.836 * 1.98847e30},
    "GJ_3090": {"tipo_espectral": "M2.5V", "masa": 0.519 * 1.98847e30},
    "GJ_4274": {"tipo_espectral": "M4.5V", "masa": 0.18 * 1.98847e30},
    "Gliese_12": {"tipo_espectral": "M4V", "masa": 0.241 * 1.98847e30},
    "Kepler_725": {"tipo_espectral": "G9V", "masa": 0.95 * 1.98847e30},
    "Gliese_514": {"tipo_espectral": "M1V", "masa": 0.510 * 1.98847e30},
    "Gliese_1002": {"tipo_espectral": "M5.5V", "masa": 0.120 * 1.98847e30},
    "Gliese_3929": {"tipo_espectral": "M4V", "masa": 0.309 * 1.98847e30},
    "HD_3167": {"tipo_espectral": "K0V", "masa": 0.870 * 1.98847e30},
    "Gaia_1": {"tipo_espectral": "G2V", "masa": 0.949 * 1.98847e30},
    "Gaia_2": {"tipo_espectral": "G2V", "masa": 1.000 * 1.98847e30},
    "Leo_Min_20": {"tipo_espectral": "G0V", "masa": 0.967 * 1.98847e30},
    "G82_Eridani": {"tipo_espectral": "G6V", "masa": 0.813 * 1.98847e30},
    "K2_72": {"tipo_espectral": "M3V", "masa": 0.27 * 1.98847e30},
    "Kepler_283": {"tipo_espectral": "K7V", "masa": 0.60 * 1.98847e30},
    "Gaia_4": {"tipo_espectral": "K7V", "masa": 0.644 * 1.98847e30},
    "HD_28185": {"tipo_espectral": "G5V", "masa": 0.974 * 1.98847e30},
    # --- Lote 3 (v5.6, sistemas multi-planeta bien caracterizados) ---
    "Kepler_90": {"tipo_espectral": "G0V", "masa": 1.20 * 1.98847e30},
    "Kepler_11": {"tipo_espectral": "G6V", "masa": 0.961 * 1.98847e30},
    "Cnc55": {"tipo_espectral": "G8V", "masa": 0.905 * 1.98847e30},
    "Kepler_20": {"tipo_espectral": "G8V", "masa": 0.912 * 1.98847e30},
    # --- Lote 4 (v5.7) ---
    "HD_110067": {"tipo_espectral": "K0V", "masa": 0.81 * 1.98847e30},
    "LHS_1140": {"tipo_espectral": "M4.5V", "masa": 0.18 * 1.98847e30},
    "LHS_475": {"tipo_espectral": "M3V", "masa": 0.27 * 1.98847e30},
    "LHS_3154": {"tipo_espectral": "M7V", "masa": 0.11 * 1.98847e30},
    "GJ_367": {"tipo_espectral": "M1V", "masa": 0.455 * 1.98847e30},
    "TOI_270": {"tipo_espectral": "M3V", "masa": 0.39 * 1.98847e30},
    "GJ_3470": {"tipo_espectral": "M1.5V", "masa": 0.51 * 1.98847e30},
    "GJ_486": {"tipo_espectral": "M3.5V", "masa": 0.32 * 1.98847e30},
    "GJ_357": {"tipo_espectral": "M2.5V", "masa": 0.342 * 1.98847e30},
    "WASP_18": {"tipo_espectral": "F6V", "masa": 1.19 * 1.98847e30},
    "WASP_19": {"tipo_espectral": "G8V", "masa": 0.935 * 1.98847e30},
    "WASP_43": {"tipo_espectral": "K7V", "masa": 0.717 * 1.98847e30},
    "WASP_76": {"tipo_espectral": "F7V", "masa": 1.458 * 1.98847e30},
    "WASP_121": {"tipo_espectral": "F6V", "masa": 1.353 * 1.98847e30},
    "WASP_127": {"tipo_espectral": "G5V", "masa": 0.95 * 1.98847e30},
    "WASP_6": {"tipo_espectral": "G8V", "masa": 0.836 * 1.98847e30},
    "WASP_31": {"tipo_espectral": "F7V", "masa": 1.161 * 1.98847e30},
    "WASP_96": {"tipo_espectral": "G8V", "masa": 1.06 * 1.98847e30},
    "HD_149026": {"tipo_espectral": "G0IV", "masa": 1.3 * 1.98847e30},
    "HD_80606": {"tipo_espectral": "G5V", "masa": 1.01 * 1.98847e30},
    "HD_17156": {"tipo_espectral": "G0V", "masa": 1.275 * 1.98847e30},
    "Kepler_16": {"tipo_espectral": "K0V+M0V(binaria)", "masa": 1.0 * 1.98847e30},
    "YZ_Ceti": {"tipo_espectral": "M4.5V", "masa": 0.13 * 1.98847e30},
    "GJ_1061": {"tipo_espectral": "M5.5V", "masa": 0.12 * 1.98847e30},
    "TOI_561": {"tipo_espectral": "K0V", "masa": 0.785 * 1.98847e30},
    "K2_141": {"tipo_espectral": "G9V", "masa": 0.708 * 1.98847e30},
    "GJ_49": {"tipo_espectral": "M1.5V", "masa": 0.54 * 1.98847e30},
    "TOI_1231": {"tipo_espectral": "M3V", "masa": 0.44 * 1.98847e30},
    "TOI_1266": {"tipo_espectral": "M3V", "masa": 0.44 * 1.98847e30},
    # --- Lote 5 (v5.8) ---
    "Kepler_9": {"tipo_espectral": "G2V", "masa": 1.0 * 1.98847e30},
    "Kepler_10": {"tipo_espectral": "G-type", "masa": 0.913 * 1.98847e30},
    "Kepler_36": {"tipo_espectral": "G-subgigante", "masa": 1.07 * 1.98847e30},
    "Kepler_37": {"tipo_espectral": "G8V", "masa": 0.803 * 1.98847e30},
    "Kepler_42": {"tipo_espectral": "M4V", "masa": 0.13 * 1.98847e30},
    "Kepler_444": {"tipo_espectral": "K0V", "masa": 0.758 * 1.98847e30},
    "Kepler_80": {"tipo_espectral": "M0V", "masa": 0.73 * 1.98847e30},
    "Kepler_102": {"tipo_espectral": "K1V", "masa": 0.809 * 1.98847e30},
    "Kepler_138": {"tipo_espectral": "M1V", "masa": 0.535 * 1.98847e30},
    "GJ_15A": {"tipo_espectral": "M2V", "masa": 0.375 * 1.98847e30},
    "GJ_176": {"tipo_espectral": "M2.5V", "masa": 0.49 * 1.98847e30},
    "GJ_179": {"tipo_espectral": "M3.5V", "masa": 0.357 * 1.98847e30},
    "GJ_3512": {"tipo_espectral": "M5.5V", "masa": 0.1237 * 1.98847e30},
    "Ross_128": {"tipo_espectral": "M4V", "masa": 0.168 * 1.98847e30},
    "HD_40307": {"tipo_espectral": "K2.5V", "masa": 0.77 * 1.98847e30},
    "Vir61": {"tipo_espectral": "G5V", "masa": 0.94 * 1.98847e30},
    "HR_858": {"tipo_espectral": "F6V", "masa": 1.19 * 1.98847e30},
    "Kepler_1544": {"tipo_espectral": "K-type", "masa": 0.81 * 1.98847e30},
    "Kepler_1652": {"tipo_espectral": "M-type", "masa": 0.463 * 1.98847e30},
    "Kepler_1638": {"tipo_espectral": "G-type", "masa": 0.98 * 1.98847e30},
    "Kepler_1606": {"tipo_espectral": "G-type", "masa": 0.95 * 1.98847e30},
    "Kepler_1090": {"tipo_espectral": "G-type", "masa": 1.06 * 1.98847e30},
    "tauBoo": {"tipo_espectral": "F7V", "masa": 1.39 * 1.98847e30},
    "UpsAnd": {"tipo_espectral": "F8V", "masa": 1.3 * 1.98847e30},
    "UMa47": {"tipo_espectral": "G0V", "masa": 1.03 * 1.98847e30},
    "HD_69830": {"tipo_espectral": "K0V", "masa": 0.86 * 1.98847e30},
    "GJ_581": {"tipo_espectral": "M3V", "masa": 0.31 * 1.98847e30},
    "Her14": {"tipo_espectral": "K0V", "masa": 0.79 * 1.98847e30},
    # --- Lote 6 (v5.9) ---
    "HD_216435": {"tipo_espectral": "G3V", "masa": 1.28 * 1.98847e30},
    "HD_154345": {"tipo_espectral": "G8V", "masa": 0.93 * 1.98847e30},
    "HD_190360": {"tipo_espectral": "G6IV", "masa": 1.04 * 1.98847e30},
    "HD_128311": {"tipo_espectral": "K0V", "masa": 0.84 * 1.98847e30},
    "HD_108874": {"tipo_espectral": "G5V", "masa": 1.0 * 1.98847e30},
    "HD_74156": {"tipo_espectral": "G0V", "masa": 1.24 * 1.98847e30},
    "HD_183263": {"tipo_espectral": "G2IV", "masa": 1.17 * 1.98847e30},
    "HD_187123": {"tipo_espectral": "G5V", "masa": 1.06 * 1.98847e30},
    "HD_12661": {"tipo_espectral": "G6V", "masa": 1.07 * 1.98847e30},
    "HD_217107": {"tipo_espectral": "G8IV", "masa": 1.02 * 1.98847e30},
    "HD_168443": {"tipo_espectral": "G6V", "masa": 1.01 * 1.98847e30},
    "Cyg16B": {"tipo_espectral": "G3V", "masa": 1.01 * 1.98847e30},
    "Kepler_56": {"tipo_espectral": "G-subgigante", "masa": 1.32 * 1.98847e30},
    "Kepler_419": {"tipo_espectral": "F-type", "masa": 1.39 * 1.98847e30},
    "Kepler_448": {"tipo_espectral": "F-type", "masa": 1.45 * 1.98847e30},
    "GJ_1148": {"tipo_espectral": "M4V", "masa": 0.36 * 1.98847e30},
    "GJ_3323": {"tipo_espectral": "M4V", "masa": 0.164 * 1.98847e30},
    "GJ_686": {"tipo_espectral": "M1V", "masa": 0.44 * 1.98847e30},
    "GJ_96": {"tipo_espectral": "K3V", "masa": 0.83 * 1.98847e30},
    "GJ_625": {"tipo_espectral": "M2V", "masa": 0.3 * 1.98847e30},
    "GJ_229A": {"tipo_espectral": "M1V", "masa": 0.58 * 1.98847e30},
    "Sex24": {"tipo_espectral": "K0III", "masa": 1.54 * 1.98847e30},
    "HD_27894": {"tipo_espectral": "K2V", "masa": 0.798 * 1.98847e30},
    "HD_37124": {"tipo_espectral": "G4V", "masa": 0.83 * 1.98847e30},
    "Kepler_296": {"tipo_espectral": "M-type", "masa": 0.5 * 1.98847e30},
    "Kepler_440": {"tipo_espectral": "K-type", "masa": 0.75 * 1.98847e30},
    "Kepler_61": {"tipo_espectral": "K-type", "masa": 0.635 * 1.98847e30},
    "Kepler_298": {"tipo_espectral": "K-type", "masa": 0.64 * 1.98847e30},
    "Kepler_1410": {"tipo_espectral": "G-type", "masa": 0.96 * 1.98847e30},
    "Kepler_1229": {"tipo_espectral": "M-type", "masa": 0.54 * 1.98847e30},
}

E_INICIAL_SISTEMA_SOLAR = {
    "Mercurio": 0.2056, "Venus": 0.0068, "Tierra": 0.0167, "Marte": 0.0934,
    "Jupiter": 0.0489, "Saturno": 0.0565, "Urano": 0.0457, "Neptuno": 0.0113,
}

# F_XUV_inicial=0.005 W/m2 (orden de magnitud del flujo XUV solar en calma
# segun Ribas et al. 2005). Con este valor la Tierra retiene ~72% de su
# atmosfera en 4.5 Gyr y Venus la retiene casi entera. Marte SI pierde la
# suya por completo (eficiencia de escape mayor, 0.5, y gravedad menor) --
# cualitativamente consistente con la perdida atmosferica real de Marte,
# aunque el modelo la predice en escalas de tiempo mas rapidas de lo
# geologicamente real. Gap documentado (igual que el caso de Jupiter en el
# modelo termico): requeriria calibrar eficiencia_escape especificamente
# contra un dato real de perdida atmosferica marciana.
PLANETAS = {
    "Mercurio": {"M": 3.285e23, "R_p": 2.439e6, "inercia": 0.35, "densidad_nucleo": 8000.0, "difusividad": 1.0, "a_inicial": 0.387 * 1.495978707e11, "w_p_inicial": 1.240e-6, "B_p_inicial": 5.0e-9, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Terrestre", "descripcion": "Planeta más cercano al Sol - Campo magnético débil", "estrella": "Sol"},
    "Venus": {"M": 4.867e24, "R_p": 6.052e6, "inercia": 0.33, "densidad_nucleo": 9500.0, "difusividad": 1.3, "a_inicial": 0.723 * 1.495978707e11, "w_p_inicial": -2.99e-7, "B_p_inicial": 1.0e-8, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Terrestre", "descripcion": "Rotación lenta - Sin campo magnético global", "estrella": "Sol",
              "R_core": 3.20e6, "T_cmb_inicial_K": 4200.0, "T_manto_inicial_K": 2100.0, "Q_cmb_hoy_W": 1.0e12,
              "k_manto": 3.5, "regimen_tectonico": 0, "albedo": 0.75,
              "M_atm_inicial": 4.8e20, "F_XUV_inicial": 0.005, "eficiencia_escape": 0.05,
              "eps_inicial_deg": 2.64, "eps_conocido": True},
    "Tierra": {"M": 5.972e24, "R_p": 6.371e6, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.0 * 1.495978707e11, "w_p_inicial": 7.292e-5, "B_p_inicial": 3.1e-5, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Terrestre", "descripcion": "Planeta de validación - Caso Tierra", "estrella": "Sol",
              "R_core": 3.485e6, "T_cmb_inicial_K": 4000.0, "T_manto_inicial_K": 2000.0, "Q_cmb_hoy_W": 4.5e12,
              "k_manto": 3.0, "regimen_tectonico": 1, "albedo": 0.3,
              "M_atm_inicial": 5.15e18, "F_XUV_inicial": 0.005, "eficiencia_escape": 0.15,
              "eps_inicial_deg": 23.44, "eps_conocido": True},
    "Marte": {"M": 6.417e23, "R_p": 3.389e6, "inercia": 0.36, "densidad_nucleo": 7000.0, "difusividad": 1.4, "a_inicial": 1.524 * 1.495978707e11, "w_p_inicial": 7.088e-5, "B_p_inicial": 1.0e-8, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Terrestre", "descripcion": "Campo magnético remanente - Atmósfera delgada", "estrella": "Sol",
              "R_core": 1.83e6, "T_cmb_inicial_K": 1950.0, "T_manto_inicial_K": 1200.0, "Q_cmb_hoy_W": 1.0e12,
              "k_manto": 2.5, "regimen_tectonico": 0, "albedo": 0.25,
              "M_atm_inicial": 2.5e16, "F_XUV_inicial": 0.005, "eficiencia_escape": 0.5,
              "eps_inicial_deg": 25.19, "eps_conocido": True},
    "Jupiter": {"M": 1.898e27, "R_p": 6.991e7, "inercia": 0.25, "densidad_nucleo": 12000.0, "difusividad": 2.5, "a_inicial": 5.203 * 1.495978707e11, "w_p_inicial": 1.758e-4, "B_p_inicial": 4.2e-4, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Campo magnético más fuerte del Sistema Solar", "estrella": "Sol",
              # GAP DOCUMENTADO: la ley de Christensen & Aubert (2006) fue derivada para
              # nucleos de hierro liquido; el hidrogeno metalico de Jupiter tiene propiedades
              # distintas. Estos valores permiten correr el modelo termico sin crashear, pero
              # el resultado NO esta validado cuantitativamente para gigantes gaseosos -- usar
              # solo como control cualitativo, igual que en v4.1.
              "R_core": 1.0e7, "T_cmb_inicial_K": 15000.0, "T_manto_inicial_K": 10000.0, "Q_cmb_hoy_W": 1.0e14,
              "k_manto": 3.0, "regimen_tectonico": 1, "albedo": 0.5,
              "eps_inicial_deg": 3.13, "eps_conocido": True},
    "Saturno": {"M": 5.683e26, "R_p": 5.823e7, "inercia": 0.26, "densidad_nucleo": 11000.0, "difusividad": 2.2, "a_inicial": 9.537 * 1.495978707e11, "w_p_inicial": 1.621e-4, "B_p_inicial": 2.1e-5, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Campo magnético moderado - Anillos", "estrella": "Sol"},
    "Urano": {"M": 8.681e25, "R_p": 2.536e7, "inercia": 0.27, "densidad_nucleo": 10000.0, "difusividad": 2.0, "a_inicial": 19.191 * 1.495978707e11, "w_p_inicial": -1.01238e-4, "B_p_inicial": 2.3e-5, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Gigante de hielo", "descripcion": "Campo magnético inclinado - Rotación inversa", "estrella": "Sol",
              "eps_inicial_deg": 97.77, "eps_conocido": True},
    "Neptuno": {"M": 1.024e26, "R_p": 2.462e7, "inercia": 0.27, "densidad_nucleo": 10500.0, "difusividad": 2.1, "a_inicial": 30.07 * 1.495978707e11, "w_p_inicial": 1.083e-4, "B_p_inicial": 1.5e-5, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "Gigante de hielo", "descripcion": "Vientos más rápidos del Sistema Solar", "estrella": "Sol"},
    "Proxima_b": {"M": 7.0e24, "R_p": 6.56e6, "inercia": 0.33, "densidad_nucleo": 7500.0, "difusividad": 1.5, "a_inicial": 0.0485 * 1.495978707e11, "w_p_inicial": 6.48e-6, "B_p_inicial": 1.5e-4, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 5.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Candidato habitable - Enana M", "estrella": "Próxima_Centauri", "e_inicial": 0.020},
    "GJ_1132b": {"M": 4.12e24, "R_p": 5.86e6, "inercia": 0.32, "densidad_nucleo": 7200.0, "difusividad": 1.6, "a_inicial": 0.0293 * 1.495978707e11, "w_p_inicial": 1.19e-5, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 4.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "Terrestre", "descripcion": "SuperTierra cercana", "estrella": "GJ_1132", "e_inicial": 0.022},
    "WASP_12b": {"M": 2.68e27, "R_p": 1.27e8, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.0, "a_inicial": 0.023 * 1.495978707e11, "w_p_inicial": 6.66e-5, "B_p_inicial": 5.0e-3, "rho_sw": 5.0e-19, "v_sw": 5.0e5, "w_estrella": 3.0e-6, "tipo_planeta": "Hot Jupiter", "descripcion": "Hot Jupiter extremo", "estrella": "WASP_12", "e_inicial": 0.003},
    "TRAPPIST_1e": {"M": 0.77 * 5.972e24, "R_p": 0.92 * 6.371e6, "inercia": 0.33, "densidad_nucleo": 7200.0, "difusividad": 1.4, "a_inicial": 0.0282 * 1.495978707e11, "w_p_inicial": 8.0e-6, "B_p_inicial": 1.3e-4, "rho_sw": 3.0e-18, "v_sw": 3.0e5, "w_estrella": 5.0e-6, "tipo_planeta": "Terrestre", "descripcion": "TRAPPIST-1 - Zona habitable", "estrella": "TRAPPIST_1", "e_inicial": 0.005},
    "Kepler_442b": {"M": 2.34 * 5.972e24, "R_p": 1.34 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 0.41 * 1.495978707e11, "w_p_inicial": 6.5e-6, "B_p_inicial": 1.3e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.5e-6, "tipo_planeta": "Terrestre", "descripcion": "Super-Tierra - Candidato habitable", "estrella": "Kepler_442"},
    "Kepler_452b": {"M": 5.0 * 5.972e24, "R_p": 1.63 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8500.0, "difusividad": 1.8, "a_inicial": 1.05 * 1.495978707e11, "w_p_inicial": 6.0e-6, "B_p_inicial": 1.5e-4, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Primer planeta del tamaño de la Tierra en zona habitable", "estrella": "Kepler_452"},
    "GJ_581c": {"M": 5.6 * 5.972e24, "R_p": 1.7 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 8600.0, "difusividad": 1.8, "a_inicial": 0.07 * 1.495978707e11, "w_p_inicial": 8.0e-6, "B_p_inicial": 1.4e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "GJ 581 - Super-Tierra en zona habitable", "estrella": "GJ_581"},
    "HD_209458b": {"M": 0.69 * 1.898e27, "R_p": 1.38 * 6.9911e7, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.2, "a_inicial": 0.047 * 1.495978707e11, "w_p_inicial": 8.0e-5, "B_p_inicial": 4.0e-3, "rho_sw": 5.0e-19, "v_sw": 5.0e5, "w_estrella": 3.0e-6, "tipo_planeta": "Hot Jupiter", "descripcion": "Hot Jupiter - Atmósfera en evaporación", "estrella": "HD_209458", "e_inicial": 0.015},
    "HD_189733b": {"M": 1.13 * 1.898e27, "R_p": 1.14 * 6.9911e7, "inercia": 0.25, "densidad_nucleo": 11500.0, "difusividad": 2.3, "a_inicial": 0.031 * 1.495978707e11, "w_p_inicial": 9.0e-5, "B_p_inicial": 4.5e-3, "rho_sw": 5.0e-19, "v_sw": 5.0e5, "w_estrella": 3.0e-6, "tipo_planeta": "Hot Jupiter", "descripcion": "Hot Jupiter - Color azul profundo", "estrella": "HD_189733", "e_inicial": 0.0041},
    "Barnard_b": {"M": 3.2 * 5.972e24, "R_p": 1.4 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 0.4 * 1.495978707e11, "w_p_inicial": 5.0e-6, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Estrella de Barnard - Planeta super-Tierra", "estrella": "Barnard"},
    "GJ_273b": {"M": 2.9 * 5.972e24, "R_p": 1.35 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8000.0, "difusividad": 1.6, "a_inicial": 0.09 * 1.495978707e11, "w_p_inicial": 7.0e-6, "B_p_inicial": 1.1e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "GJ 273 - Planeta en zona habitable", "estrella": "GJ_273"},
    "Teegarden_b": {"M": 1.05 * 5.972e24, "R_p": 1.02 * 6.371e6, "inercia": 0.33, "densidad_nucleo": 7600.0, "difusividad": 1.5, "a_inicial": 0.025 * 1.495978707e11, "w_p_inicial": 1.0e-5, "B_p_inicial": 1.1e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Teegarden - Candidato habitable", "estrella": "Teegarden", "e_inicial": 0.030},
    "Teegarden_c": {"M": 1.11 * 5.972e24, "R_p": 1.04 * 6.371e6, "inercia": 0.33, "densidad_nucleo": 7700.0, "difusividad": 1.5, "a_inicial": 0.044 * 1.495978707e11, "w_p_inicial": 8.0e-6, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Teegarden - Segundo planeta", "estrella": "Teegarden", "e_inicial": 0.040},
    "Luyten_b": {"M": 2.89 * 5.972e24, "R_p": 1.35 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8000.0, "difusividad": 1.6, "a_inicial": 0.09 * 1.495978707e11, "w_p_inicial": 7.0e-6, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Luyten - Candidato habitable", "estrella": "Luyten"},
    "Wolf_1061c": {"M": 4.3 * 5.972e24, "R_p": 1.5 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8400.0, "difusividad": 1.7, "a_inicial": 0.09 * 1.495978707e11, "w_p_inicial": 7.0e-6, "B_p_inicial": 1.2e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Wolf 1061 - Candidato habitable", "estrella": "Wolf_1061"},
    "Gliese_667Cc": {"M": 4.5 * 5.972e24, "R_p": 1.55 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8400.0, "difusividad": 1.7, "a_inicial": 0.12 * 1.495978707e11, "w_p_inicial": 6.5e-6, "B_p_inicial": 1.2e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Uno de los mejores candidatos habitables", "estrella": "Gliese_667"},
    "Gliese_832c": {"M": 5.4 * 5.972e24, "R_p": 1.65 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 8500.0, "difusividad": 1.8, "a_inicial": 0.16 * 1.495978707e11, "w_p_inicial": 6.0e-6, "B_p_inicial": 1.3e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Gliese 832 - Super-Tierra en zona habitable", "estrella": "Gliese_832"},
    "Kepler_186f": {"M": 1.44 * 5.972e24, "R_p": 1.17 * 6.371e6, "inercia": 0.33, "densidad_nucleo": 7900.0, "difusividad": 1.6, "a_inicial": 0.39 * 1.495978707e11, "w_p_inicial": 7.0e-6, "B_p_inicial": 1.2e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.5e-6, "tipo_planeta": "Terrestre", "descripcion": "Primer exoplaneta en zona habitable", "estrella": "Kepler_186"},
    "Kepler_62f": {"M": 2.8 * 5.972e24, "R_p": 1.41 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8000.0, "difusividad": 1.6, "a_inicial": 0.72 * 1.495978707e11, "w_p_inicial": 5.5e-6, "B_p_inicial": 1.1e-4, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Candidato habitable - Sistema Kepler-62", "estrella": "Kepler_62"},
    "Kepler_69c": {"M": 2.5 * 5.972e24, "R_p": 1.35 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8100.0, "difusividad": 1.6, "a_inicial": 0.64 * 1.495978707e11, "w_p_inicial": 5.8e-6, "B_p_inicial": 1.0e-4, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Candidato habitable - Super-Tierra", "estrella": "Kepler_69"},
    "Kepler_22b": {"M": 2.4 * 5.972e24, "R_p": 1.32 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8000.0, "difusividad": 1.6, "a_inicial": 0.85 * 1.495978707e11, "w_p_inicial": 6.0e-6, "B_p_inicial": 1.2e-4, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Primer exoplaneta en zona habitable confirmado", "estrella": "Kepler_22"},
    "Kepler_1649c": {"M": 1.06 * 5.972e24, "R_p": 1.02 * 6.371e6, "inercia": 0.33, "densidad_nucleo": 7600.0, "difusividad": 1.5, "a_inicial": 0.06 * 1.495978707e11, "w_p_inicial": 8.0e-6, "B_p_inicial": 1.1e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Similar a Tierra en tamaño y flujo", "estrella": "Kepler_1649"},
    "TOI_700d": {"M": 1.72 * 5.972e24, "R_p": 1.19 * 6.371e6, "inercia": 0.33, "densidad_nucleo": 7900.0, "difusividad": 1.6, "a_inicial": 0.16 * 1.495978707e11, "w_p_inicial": 6.0e-6, "B_p_inicial": 1.2e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "Terrestre", "descripcion": "TOI-700 - Candidato habitable", "estrella": "TOI_700"},
    "Tau_Ceti_e": {"M": 4.3 * 5.972e24, "R_p": 1.5 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8400.0, "difusividad": 1.7, "a_inicial": 0.55 * 1.495978707e11, "w_p_inicial": 6.0e-6, "B_p_inicial": 1.2e-4, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Tau Ceti - Sistema cercano con múltiples planetas", "estrella": "Tau_Ceti"},
    "GJ_180_b": {"M": 3.0 * 5.972e24, "R_p": 1.38 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8100.0, "difusividad": 1.6, "a_inicial": 0.12 * 1.495978707e11, "w_p_inicial": 6.5e-6, "B_p_inicial": 1.1e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "GJ 180 - Zona habitable", "estrella": "GJ_180"},
    "GJ_422_b": {"M": 3.5 * 5.972e24, "R_p": 1.42 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.6, "a_inicial": 0.15 * 1.495978707e11, "w_p_inicial": 6.0e-6, "B_p_inicial": 1.1e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "GJ 422 - Cercano, zona habitable", "estrella": "GJ_422"},
    "K2_18b": {"M": 8.6 * 5.972e24, "R_p": 2.6 * 6.371e6, "inercia": 0.30, "densidad_nucleo": 7500.0, "difusividad": 1.6, "a_inicial": 0.14 * 1.495978707e11, "w_p_inicial": 8.0e-6, "B_p_inicial": 1.2e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.5e-6, "tipo_planeta": "SubNeptuno", "descripcion": "K2-18 - Sub-Neptuno con agua", "estrella": "K2_18"},
    "K2_18c": {"M": 5.0 * 5.972e24, "R_p": 1.8 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 0.15 * 1.495978707e11, "w_p_inicial": 7.0e-6, "B_p_inicial": 1.0e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.5e-6, "tipo_planeta": "SuperTierra", "descripcion": "K2-18 - Planeta compañero", "estrella": "K2_18"},
    "HD_40307g": {"M": 7.1 * 5.972e24, "R_p": 1.8 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 8700.0, "difusividad": 1.8, "a_inicial": 0.22 * 1.495978707e11, "w_p_inicial": 8.0e-6, "B_p_inicial": 1.6e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra - Zona habitable", "estrella": "HD_40307"},
    "HD_85512b": {"M": 3.6 * 5.972e24, "R_p": 1.45 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.6, "a_inicial": 0.26 * 1.495978707e11, "w_p_inicial": 7.0e-6, "B_p_inicial": 1.3e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Candidato habitable - Super-Tierra", "estrella": "HD_85512"},
    "GJ_1214b": {"M": 6.6 * 5.972e24, "R_p": 2.7 * 6.371e6, "inercia": 0.30, "densidad_nucleo": 7500.0, "difusividad": 1.6, "a_inicial": 0.014 * 1.495978707e11, "w_p_inicial": 1.3e-5, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Mundo acuático - Sub-Neptuno", "estrella": "GJ_1214"},
    "55_Cancri_e": {"M": 8.6 * 5.972e24, "R_p": 2.0 * 6.371e6, "inercia": 0.30, "densidad_nucleo": 8800.0, "difusividad": 1.8, "a_inicial": 0.015 * 1.495978707e11, "w_p_inicial": 1.4e-5, "B_p_inicial": 1.5e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra - Diamante posible", "estrella": "55_Cancri"},
    "WASP_17b": {"M": 0.48 * 1.898e27, "R_p": 1.99 * 6.9911e7, "inercia": 0.24, "densidad_nucleo": 10000.0, "difusividad": 2.0, "a_inicial": 0.05 * 1.495978707e11, "w_p_inicial": 7.5e-5, "B_p_inicial": 3.5e-3, "rho_sw": 5.0e-19, "v_sw": 5.0e5, "w_estrella": 3.0e-6, "tipo_planeta": "Hot Jupiter", "descripcion": "Hot Jupiter - Órbita retrógrada", "estrella": "WASP_17", "e_inicial": 0.020},
    "WASP_39b": {"M": 0.28 * 1.898e27, "R_p": 1.27 * 6.9911e7, "inercia": 0.25, "densidad_nucleo": 10000.0, "difusividad": 2.0, "a_inicial": 0.05 * 1.495978707e11, "w_p_inicial": 7.0e-5, "B_p_inicial": 3.0e-3, "rho_sw": 5.0e-19, "v_sw": 5.0e5, "w_estrella": 3.0e-6, "tipo_planeta": "Hot Jupiter", "descripcion": "Hot Jupiter - Atmósfera con agua", "estrella": "WASP_39", "e_inicial": 0.010},
    "CoRoT_7b": {"M": 4.8 * 5.972e24, "R_p": 1.6 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8500.0, "difusividad": 1.7, "a_inicial": 0.017 * 1.495978707e11, "w_p_inicial": 1.2e-5, "B_p_inicial": 1.5e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra - Lava en superficie", "estrella": "CoRoT_7"},
    "EPIC_201912552b": {"M": 4.5 * 5.972e24, "R_p": 1.5 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8300.0, "difusividad": 1.7, "a_inicial": 0.02 * 1.495978707e11, "w_p_inicial": 1.1e-5, "B_p_inicial": 1.2e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema con tránsitos múltiples", "estrella": "EPIC_201912552"},
    "K2_3d": {"M": 2.0 * 5.972e24, "R_p": 1.2 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 7800.0, "difusividad": 1.6, "a_inicial": 0.12 * 1.495978707e11, "w_p_inicial": 6.5e-6, "B_p_inicial": 1.1e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.5e-6, "tipo_planeta": "SuperTierra", "descripcion": "K2-3 - Zona habitable", "estrella": "K2_3", "e_inicial": 0.020},
    "HD_219134b": {"M": 4.74 * 5.972e24, "R_p": 1.6 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8500.0, "difusividad": 1.7, "a_inicial": 0.038 * 1.495978707e11, "w_p_inicial": 1.0e-5, "B_p_inicial": 1.5e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra - Tránsito múltiple", "estrella": "HD_219134"},
    "GJ_3293b": {"M": 3.0 * 5.972e24, "R_p": 1.38 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8100.0, "difusividad": 1.6, "a_inicial": 0.12 * 1.495978707e11, "w_p_inicial": 6.5e-6, "B_p_inicial": 1.2e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "GJ 3293 - Planeta en zona habitable", "estrella": "GJ_3293"},

    # ========================================================================
    # LOTE 1 (v5.4) -- 10 exoplanetas confirmados 2025-2026, datos reales de
    # M/R_p/P_orbital/a con fuente citada por planeta. fuente_orbital="real"
    # declarado explicitamente en cada uno (no via la lista congelada de v5.4,
    # que solo cubre los 47 planetas previos).
    #
    # Convenciones seguidas (iguales a los 39 exoplanetas previos, no un
    # estandar mas laxo):
    #   - w_p_inicial: rotacion sincrona asumida (w = 2*pi/P_orbital) para
    #     todos -- son planetas de periodo corto (<5 dias), misma logica ya
    #     usada en WASP_12b/HD_209458b/etc. NO es un dato medido de rotacion
    #     planetaria real (no existe tal medicion para ningun exoplaneta).
    #   - B_p_inicial: SIN medicion real para ningun exoplaneta de este lote
    #     (como en el resto de la base) -- valor de categoria SuperTierra/
    #     SubNeptuno ya usado en otros planetas del archivo (1.0-1.5e-4 T).
    #   - inercia/densidad_nucleo/difusividad: valores de categoria, mismo
    #     patron que el resto del archivo, NO medidos.
    #   - a_inicial: real cuando el paper lo reporta directo; derivado via
    #     3ra ley de Kepler (con masa estelar aproximada por tipo espectral)
    #     cuando el paper solo reporta periodo -- marcado por planeta.
    # ========================================================================

    "TOI_4616b": {"M": 2.25 * 5.972e24, "R_p": 1.22 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8500.0, "difusividad": 1.6, "a_inicial": 0.01534 * 1.495978707e11, "w_p_inicial": 4.69e-5, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Terrestre benchmark - M4 dwarf cercana (91.8 al)", "estrella": "TOI_4616", "fuente_orbital": "real",
                 # M/R_p/P reales: Zong Lang et al. 2026 (arXiv:2603.10905). Masa
                 # rango 1.5-3.0 M_tierra en el paper, se usa punto medio 2.25.
                 # a_inicial DERIVADO via Kepler (masa estelar aprox. por tipo M4V,
                 # no medida directamente para esta estrella) -- no es dato directo.
                 },
    "TOI_2431b": {"M": 6.2 * 5.972e24, "R_p": 1.536 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 11000.0, "difusividad": 1.5, "a_inicial": 0.0063 * 1.495978707e11, "w_p_inicial": 3.244e-4, "B_p_inicial": 1.2e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SuperTierra", "descripcion": "Planeta ultra-denso (9.4 g/cm3) - periodo ultra-corto 5h22min", "estrella": "TOI_2431", "e_inicial": 0.0, "fuente_orbital": "real",
                 # M/R_p/a/P/e reales: Tas et al. 2025. densidad_nucleo elevada
                 # (11000) refleja la densidad bulk medida muy alta, no es
                 # categoria generica.
                 },
    "TOI_1243b": {"M": 7.7 * 5.972e24, "R_p": 2.33 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 7500.0, "difusividad": 1.6, "a_inicial": 0.03846 * 1.495978707e11, "w_p_inicial": 1.560e-5, "B_p_inicial": 1.1e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno alrededor de enana M cercana", "estrella": "TOI_1243_host", "fuente_orbital": "real",
                  # M/R_p/P reales: Poultourtzidis et al. 2026 (arXiv:2601.07414).
                  # a_inicial DERIVADO via Kepler (masa estelar aproximada).
                  },
    "TOI_3862b": {"M": 53.7 * 5.972e24, "R_p": 5.53 * 6.371e6, "inercia": 0.29, "densidad_nucleo": 7000.0, "difusividad": 1.8, "a_inicial": 0.025 * 1.495978707e11, "w_p_inicial": 4.661e-5, "B_p_inicial": 1.5e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.9e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Super-Neptuno denso en el 'desierto Neptuniano caliente'", "estrella": "TOI_3862", "fuente_orbital": "real",
                  # M/R_p/P/a reales: Carleo et al. 2026 (arXiv:2601.10450).
                  # Nucleo de hierro 38-41% + manto silicato 40-45% segun el
                  # paper -- densidad_nucleo/inercia ajustados a ese perfil
                  # (mas denso que un SubNeptuno tipico), no valor generico.
                  },
    "TOI_3785b": {"M": 14.95 * 5.972e24, "R_p": 5.14 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 6500.0, "difusividad": 1.9, "a_inicial": 0.04028 * 1.495978707e11, "w_p_inicial": 1.557e-5, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Neptuno de baja densidad (0.61 g/cm3) - enana M2", "estrella": "TOI_3785", "fuente_orbital": "real",
                  # M/R_p/P reales (arXiv:2304.04730). a_inicial DERIVADO via
                  # Kepler. Densidad muy baja del paper -> densidad_nucleo mas
                  # baja que el default SubNeptuno generico.
                  },
    "TOI_3568b": {"M": 26.4 * 5.972e24, "R_p": 5.30 * 6.371e6, "inercia": 0.30, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 0.04789 * 1.495978707e11, "w_p_inicial": 1.646e-5, "B_p_inicial": 1.2e-4, "rho_sw": 5.0e-19, "v_sw": 4.0e5, "w_estrella": 2.9e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Super-Neptuno en el 'desierto sub-Joviano'", "estrella": "TOI_3568", "fuente_orbital": "real",
                  # M/R_p/P reales (NTRS 2024, arXiv previo a A&A 2026). a_inicial
                  # DERIVADO via Kepler.
                  },
    "TOI_4495b": {"M": 7.7 * 5.972e24, "R_p": 2.48 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 7800.0, "difusividad": 1.7, "a_inicial": 0.03957 * 1.495978707e11, "w_p_inicial": 2.833e-5, "B_p_inicial": 1.1e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.5e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno interior, casi-resonante 2:1 con TOI_4495c", "estrella": "TOI_4495", "e_inicial": 0.03, "fuente_orbital": "real",
                  # M/R_p/a/P reales: Wang et al. 2026 (arXiv:2601.02665) via
                  # NASA Exoplanet Archive. e_inicial ESTIMADO (paper reporta
                  # excitacion de excentricidad ~4% del sistema, no un valor
                  # puntual preciso para b individualmente) -- no confundir con
                  # los demas campos, que si son directos del paper.
                  },
    "TOI_4495c": {"M": 23.2 * 5.972e24, "R_p": 4.03 * 6.371e6, "inercia": 0.30, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 0.06386 * 1.495978707e11, "w_p_inicial": 1.402e-5, "B_p_inicial": 1.3e-4, "rho_sw": 1.0e-19, "v_sw": 3.5e5, "w_estrella": 2.5e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Neptuno-like exterior, casi-resonante 2:1 con TOI_4495b", "estrella": "TOI_4495", "e_inicial": 0.03, "fuente_orbital": "real",
                  # M/R_p/P reales (mismo paper que TOI_4495b). a_inicial
                  # DERIVADO via Kepler. e_inicial ESTIMADO (ver nota en b).
                  },
    "TOI_654b": {"M": 8.71 * 5.972e24, "R_p": 2.378 * 6.371e6, "inercia": 0.31, "densidad_nucleo": 7600.0, "difusividad": 1.6, "a_inicial": 0.01739 * 1.495978707e11, "w_p_inicial": 4.753e-5, "B_p_inicial": 1.1e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno corto periodo en borde del 'radius valley'", "estrella": "TOI_654", "fuente_orbital": "real",
                 # M/R_p/P reales (arXiv:2507.16222). a_inicial DERIVADO via
                 # Kepler.
                 },
    "Barnard_c": {"M": 0.334 * 5.972e24, "R_p": 0.744 * 6.371e6, "inercia": 0.33, "densidad_nucleo": 8500.0, "difusividad": 1.3, "a_inicial": 0.0274 * 1.495978707e11, "w_p_inicial": 1.766e-5, "B_p_inicial": 5.0e-9, "rho_sw": 5.0e-21, "v_sw": 4.0e5, "w_estrella": 5.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sub-Tierra, vecina cercana (5.96 al) - deteccion RV", "estrella": "Barnard", "fuente_orbital": "real",
                  # M/a/P reales (deteccion RV, masa minima). Distancia real:
                  # 5.96 anios luz. R_p ESTIMADO via relacion masa-radio para
                  # rocosos (R ~ M^0.27) -- NO medido, deteccion RV no da
                  # radio directo. Confirmacion de 2025, mas reciente/menos
                  # establecida que Barnard_b (2018).
                  },

    "GJ_523b": {"M": 1.402549e+26, "R_p": 1.624780e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.834070e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno templado, estrella K5V a 86.8 al", "estrella": "GJ_523", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_887d": {"M": 3.643971e+25, "R_p": 1.492655e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.171475e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Super-Tierra en zona habitable de GJ 887 (10.7 al)", "estrella": "GJ_887", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_887e": {"M": 8.730347e+24, "R_p": 7.284729e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 6.238231e+09, "w_p_inicial": 1.643473e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Companero interior de GJ 887 d, periodo ultra-corto", "estrella": "GJ_887", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_1137c": {"M": 3.057664e+25, "R_p": 9.901717e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.249142e+10, "w_p_inicial": 7.542842e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra RV, radio estimado (sin transito)", "estrella": "GJ_1137", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_3090b": {"M": 1.992797e+25, "R_p": 1.356959e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 4.734773e+09, "w_p_inicial": 2.548875e-05, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno interior, sistema multi-planeta GJ 3090", "estrella": "GJ_3090", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_3090c": {"M": 1.021071e+26, "R_p": 1.999729e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.491491e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno exterior del sistema GJ 3090", "estrella": "GJ_3090", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_4274b": {"M": 1.765048e+25, "R_p": 9.955796e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 2.288847e+09, "w_p_inicial": 4.450826e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra ultra-corto periodo, enana M4.5", "estrella": "GJ_4274", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_4274c": {"M": 5.010460e+25, "R_p": 1.799757e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.782520e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno exterior del sistema GJ 4274", "estrella": "GJ_4274", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Gliese_12b": {"M": 5.255360e+24, "R_p": 6.371000e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 9.873459e+09, "w_p_inicial": 5.726146e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Terrestre templado (315K), muy estudiado por JWST", "estrella": "Gliese_12", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_725c": {"M": 5.972000e+25, "R_p": 1.186336e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.008290e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra en zona habitable de estrella tipo Sol, detectada via TTV", "estrella": "Kepler_725", "e_inicial": 0.44, "fuente_orbital": "real"},
    "Gliese_514b": {"M": 3.111412e+25, "R_p": 9.948413e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 6.313030e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra en borde de zona habitable", "estrella": "Gliese_514", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Gliese_1002b": {"M": 6.449760e+24, "R_p": 6.504771e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 6.836623e+09, "w_p_inicial": 7.028662e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Terrestre en zona habitable, enana M ultra-fria", "estrella": "Gliese_1002", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Gliese_1002c": {"M": 8.181640e+24, "R_p": 6.936209e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.104032e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Terrestre exterior en zona habitable, mismo sistema", "estrella": "Gliese_1002", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Gliese_3929b": {"M": 1.045100e+25, "R_p": 6.931648e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 3.769866e+09, "w_p_inicial": 2.779603e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Terrestre transitante, periodo corto", "estrella": "Gliese_3929", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Gliese_3929c": {"M": 3.415984e+25, "R_p": 1.020245e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.211743e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra exterior del sistema Gliese 3929", "estrella": "Gliese_3929", "e_inicial": 0.0, "fuente_orbital": "real"},
    "HD_3167e": {"M": 5.804784e+25, "R_p": 1.177274e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 6.055722e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra RV en sistema multi-planeta conocido", "estrella": "HD_3167", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Gaia_1b": {"M": 3.188475e+27, "R_p": 8.777384e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.054226e+09, "w_p_inicial": 2.382358e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter, primer exoplaneta confirmado por Gaia", "estrella": "Gaia_1", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Gaia_2b": {"M": 1.550586e+27, "R_p": 9.441580e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.986221e+09, "w_p_inicial": 1.969975e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter, segundo exoplaneta confirmado por Gaia", "estrella": "Gaia_2", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Leo_Min_20b": {"M": 5.469752e+25, "R_p": 1.158528e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.866295e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno RV, radio estimado", "estrella": "Leo_Min_20", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "G82_Eridani_d": {"M": 3.475058e+25, "R_p": 1.024979e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.025555e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno en zona habitable, vecina cercana (19.7 al)", "estrella": "G82_Eridani", "e_inicial": 0.0, "fuente_orbital": "real"},
    "K2_72e": {"M": 1.319812e+25, "R_p": 8.218590e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.585737e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra transitante en sistema multi-planeta K2-72", "estrella": "K2_72", "e_inicial": 0.11, "fuente_orbital": "real"},
    "K2_72c": {"M": 3.404040e+24, "R_p": 5.479060e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.080097e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Terrestre en borde interior de zona habitable, sistema K2-72", "estrella": "K2_72", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_283c": {"M": 3.284600e+25, "R_p": 1.159522e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 5.028643e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno transitante, masa estimada", "estrella": "Kepler_283", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Gaia_4b": {"M": 2.239524e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.740721e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante masivo cerca del limite de enana marron (astrometria+RV)", "estrella": "Gaia_4", "e_inicial": 0.0, "fuente_orbital": "real"},
    "HD_28185c": {"M": 1.078008e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.277566e+12, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante gaseoso de periodo largo (~25 anios), analogo frio", "estrella": "HD_28185", "e_inicial": 0.0, "fuente_orbital": "real"},

    # ========================================================================
    # LOTE 3 (v5.6) -- 50 exoplanetas de sistemas multi-planeta bien
    # caracterizados: TRAPPIST-1 (6), Kepler-90 (8), Kepler-11 (6),
    # 55 Cancri (4), Kepler-62 (4), HD 219134 (4), Proxima Centauri (2),
    # TOI-700 (3), Wolf 1061 (2), K2-3 (2), Kepler-186 (4), Kepler-20 (5).
    # Fuente: Wikipedia (paginas individuales por planeta, basadas en NASA
    # Exoplanet Archive) + Agol et al. 2021 (TRAPPIST-1) + Weiss et al. 2024/
    # 2025 (masas Kepler-90 g/h via TTV+RV).
    #
    # ADVERTENCIA DE HONESTIDAD: en sistemas Kepler puramente transitantes
    # (Kepler-62, Kepler-90 b/c/d/i, Kepler-186, Kepler-20 e/f) NO hay masa
    # medida -- se estima via relacion masa-radio, marcado "[M estimada]" en
    # cada planeta. En sistemas puramente RV sin transito propio (55 Cancri
    # b/c/d/f, HD 219134 d/f/h, Proxima c/d, Wolf 1061 b/d) NO hay radio
    # medido -- estimado via la misma relacion, marcado "[R estimado]".
    # w_p_inicial: sincrono solo para periodos cortos en estrellas de baja
    # masa (mismo criterio que Lotes 1 y 2); el resto usa el placeholder
    # generico 7.0e-6 rad/s.
    # ========================================================================

    "TRAPPIST_1b": {"M": 8.205528e+24, "R_p": 7.110036e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.726359e+09, "w_p_inicial": 4.813397e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Interior del sistema TRAPPIST-1, probable capa volatil [todo real]", "estrella": "TRAPPIST_1", "e_inicial": 0.0062, "fuente_orbital": "real"},
    "TRAPPIST_1c": {"M": 7.811376e+24, "R_p": 6.988987e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.363646e+09, "w_p_inicial": 3.002640e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Rocoso, posible atmosfera fina/inexistente [todo real]", "estrella": "TRAPPIST_1", "e_inicial": 0.0065, "fuente_orbital": "real"},
    "TRAPPIST_1d": {"M": 2.317136e+24, "R_p": 5.020348e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 3.331545e+09, "w_p_inicial": 1.795953e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "El mas pequeno del sistema, densidad menor [todo real]", "estrella": "TRAPPIST_1", "e_inicial": 0.0084, "fuente_orbital": "real"},
    "TRAPPIST_1f": {"M": 6.204908e+24, "R_p": 6.657695e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 5.758022e+09, "w_p_inicial": 7.898098e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Zona habitable de TRAPPIST-1, probable capa volatil [todo real]", "estrella": "TRAPPIST_1", "e_inicial": 0.0101, "fuente_orbital": "real"},
    "TRAPPIST_1g": {"M": 7.889012e+24, "R_p": 7.192859e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 7.005668e+09, "w_p_inicial": 5.887259e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Zona habitable de TRAPPIST-1, probable capa volatil [todo real]", "estrella": "TRAPPIST_1", "e_inicial": 0.0021, "fuente_orbital": "real"},
    "TRAPPIST_1h": {"M": 1.946872e+24, "R_p": 4.810105e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 9.258612e+09, "w_p_inicial": 3.873785e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Exterior del sistema, mas frio, probable hielo [todo real]", "estrella": "TRAPPIST_1", "e_inicial": 0.0057, "fuente_orbital": "real"},
    "Kepler_90b": {"M": 1.621898e+25, "R_p": 8.346010e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.107024e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Interior del sistema Kepler-90 (8 planetas, resonante) [M estimada]", "estrella": "Kepler_90", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_90c": {"M": 1.136694e+25, "R_p": 7.581490e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.331421e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-90, masa estimada via relacion masa-radio [M estimada]", "estrella": "Kepler_90", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_90d": {"M": 4.231790e+25, "R_p": 1.834848e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 4.787132e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-90, masa estimada via relacion masa-radio [M estimada]", "estrella": "Kepler_90", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_90i": {"M": 1.668182e+25, "R_p": 8.409720e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.600697e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Descubierto via deep learning (Shallue et al 2017) [M estimada]", "estrella": "Kepler_90", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_90e": {"M": 3.372265e+25, "R_p": 1.694686e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 6.283111e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-90, masa estimada via relacion masa-radio [M estimada]", "estrella": "Kepler_90", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_90f": {"M": 4.231790e+25, "R_p": 1.834848e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 7.180698e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-90, masa estimada via relacion masa-radio [M estimada]", "estrella": "Kepler_90", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_90g": {"M": 8.958000e+25, "R_p": 5.160510e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.062145e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Densidad extremadamente baja (0.15 g/cm3), masa real via TTV/RV [todo real]", "estrella": "Kepler_90", "e_inicial": 0.049, "fuente_orbital": "real"},
    "Kepler_90h": {"M": 1.212759e+27, "R_p": 7.169030e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.510938e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante exterior del sistema, masa real via TTV/RV 2025 [todo real]", "estrella": "Kepler_90", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_11b": {"M": 1.660216e+25, "R_p": 1.165893e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.361341e+10, "w_p_inicial": 7.057824e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema ultra-compacto de 6 planetas (todos entre Mercurio y Venus) [todo real]", "estrella": "Kepler_11", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_11c": {"M": 8.062200e+25, "R_p": 2.006865e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.585737e+10, "w_p_inicial": 5.583258e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema ultra-compacto Kepler-11 [todo real]", "estrella": "Kepler_11", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_11d": {"M": 3.642920e+25, "R_p": 2.185253e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.378606e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema ultra-compacto Kepler-11, baja densidad [todo real]", "estrella": "Kepler_11", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_11e": {"M": 5.016480e+25, "R_p": 2.879692e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.902199e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema ultra-compacto Kepler-11, envolvente H/He significativa [todo real]", "estrella": "Kepler_11", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_11f": {"M": 1.373560e+25, "R_p": 1.662831e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.739947e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "El menos masivo del sistema Kepler-11 [todo real]", "estrella": "Kepler_11", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_11g": {"M": 8.393055e+25, "R_p": 2.331786e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 6.911422e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Exterior del sistema, masa/radio con mayor incertidumbre [M estimada]", "estrella": "Kepler_11", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Cnc55_b": {"M": 1.563871e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.696440e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante interior del sistema 55 Cancri, radio estimado (RV) [R estimado]", "estrella": "Cnc55", "e_inicial": 0.0096, "fuente_orbital": "estimado"},
    "Cnc55_c": {"M": 3.206964e+26, "R_p": 2.424606e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.549957e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno del sistema 55 Cancri, radio estimado (RV) [R estimado]", "estrella": "Cnc55", "e_inicial": 0.005, "fuente_orbital": "estimado"},
    "Cnc55_d": {"M": 7.360062e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 8.911545e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante exterior de periodo largo (~15 anios), radio estimado (RV) [R estimado]", "estrella": "Cnc55", "e_inicial": 0.13, "fuente_orbital": "estimado"},
    "Cnc55_f": {"M": 2.806840e+26, "R_p": 2.345158e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.168359e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno en el sistema 55 Cancri, radio estimado (RV) [R estimado]", "estrella": "Cnc55", "e_inicial": 0.08, "fuente_orbital": "estimado"},
    "Kepler_62b": {"M": 1.621898e+25, "R_p": 8.346010e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 8.272762e+09, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-62 (5 planetas), masa estimada [M estimada]", "estrella": "Kepler_62", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_62c": {"M": 6.109093e+23, "R_p": 3.440340e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.391260e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "El mas pequeno del sistema Kepler-62, masa estimada [M estimada]", "estrella": "Kepler_62", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_62d": {"M": 1.388815e+25, "R_p": 1.242345e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.795174e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema Kepler-62, masa estimada [M estimada]", "estrella": "Kepler_62", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_62e": {"M": 8.033507e+24, "R_p": 1.025731e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 6.387829e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Zona habitable de Kepler-62, masa estimada [M estimada]", "estrella": "Kepler_62", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_219134c": {"M": 2.830728e+25, "R_p": 9.626581e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 9.693942e+09, "w_p_inicial": 1.074975e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema HD 219134 (hasta 6 planetas), rocoso confirmado [todo real]", "estrella": "HD_219134", "e_inicial": 0.0, "fuente_orbital": "real"},
    "HD_219134d": {"M": 9.656724e+25, "R_p": 1.796078e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.545470e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 219134, radio estimado (RV, masa minima) [R estimado]", "estrella": "HD_219134", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_219134f": {"M": 4.359560e+25, "R_p": 1.089695e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 2.188617e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema HD 219134, radio estimado (RV, masa minima) [R estimado]", "estrella": "HD_219134", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_219134h": {"M": 6.452865e+26, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.652494e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante exterior de periodo largo, radio estimado (RV) [R estimado]", "estrella": "HD_219134", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Proxima_c": {"M": 4.180400e+25, "R_p": 1.077418e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 2.227512e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Candidato de periodo largo, algo disputado, radio estimado [R estimado]", "estrella": "Próxima_Centauri", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Proxima_d": {"M": 1.552720e+24, "R_p": 4.428436e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 4.315899e+09, "w_p_inicial": 1.412079e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sub-Tierra ultra-corto periodo, confirmado ESPRESSO 2022 [R estimado]", "estrella": "Próxima_Centauri", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "TOI_700b": {"M": 5.541869e+24, "R_p": 6.243580e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 9.529384e+09, "w_p_inicial": 7.286779e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema TOI-700 (4 planetas), interior [M estimada]", "estrella": "TOI_700", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "TOI_700c": {"M": 3.336169e+25, "R_p": 1.688315e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.298510e+10, "w_p_inicial": 4.530969e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema TOI-700, SubNeptuno [M estimada]", "estrella": "TOI_700", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "TOI_700e": {"M": 4.939661e+24, "R_p": 6.052450e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.989652e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema TOI-700, terrestre [M estimada]", "estrella": "TOI_700", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Wolf_1061b": {"M": 8.121920e+24, "R_p": 6.922502e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 5.310724e+09, "w_p_inicial": 1.488071e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Interior del sistema Wolf 1061, radio estimado (RV) [R estimado]", "estrella": "Wolf_1061", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Wolf_1061d": {"M": 3.111412e+25, "R_p": 9.948413e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 3.014397e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Exterior del sistema Wolf 1061, radio estimado (RV) [R estimado]", "estrella": "Wolf_1061", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "K2_3b": {"M": 1.811396e+25, "R_p": 1.363394e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.107024e+10, "w_p_inicial": 7.236025e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema K2-3 (3 planetas), interior [M estimada]", "estrella": "K2_3", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "K2_3c": {"M": 1.053099e+25, "R_p": 1.127667e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.094370e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema K2-3, intermedio [M estimada]", "estrella": "K2_3", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_186b": {"M": 7.408862e+24, "R_p": 6.753260e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 5.131207e+09, "w_p_inicial": 1.870904e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-186 (5 planetas), interior, masa estimada [M estimada]", "estrella": "Kepler_186", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_186c": {"M": 1.363600e+25, "R_p": 7.963750e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 8.586918e+09, "w_p_inicial": 1.000716e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-186, masa estimada [M estimada]", "estrella": "Kepler_186", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_186d": {"M": 2.019643e+25, "R_p": 8.855690e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.352365e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-186, masa estimada [M estimada]", "estrella": "Kepler_186", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_186e": {"M": 1.668182e+25, "R_p": 8.409720e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.908869e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-186, masa estimada [M estimada]", "estrella": "Kepler_186", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_20b": {"M": 5.195640e+25, "R_p": 1.216861e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 6.731904e+09, "w_p_inicial": 1.967588e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema Kepler-20 (5 planetas) [todo real]", "estrella": "Kepler_20", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_20c": {"M": 9.376040e+25, "R_p": 1.955897e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.391260e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-20 [todo real]", "estrella": "Kepler_20", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_20d": {"M": 1.194400e+26, "R_p": 1.752025e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 5.235925e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-20, masa poco restringida (limite superior RV) [todo real]", "estrella": "Kepler_20", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_20e": {"M": 3.537063e+24, "R_p": 5.530028e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 8.407400e+09, "w_p_inicial": 1.192556e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Tamano casi-terrestre, masa estimada [M estimada]", "estrella": "Kepler_20", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_20f": {"M": 6.662198e+24, "R_p": 6.562130e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.660536e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Tamano casi-terrestre, masa estimada [M estimada]", "estrella": "Kepler_20", "e_inicial": 0.0, "fuente_orbital": "estimado"},

    # ========================================================================
    # LOTE 4 (v5.7) -- 50 exoplanetas: HD 110067 (cadena resonante 6
    # subneptunos), LHS 1140/475/3154, GJ 367 (planeta de hierro), TOI-270,
    # GJ 3470/486/357, 9 hot Jupiters WASP, 3 gigantes HD (incluye HD 80606b
    # de excentricidad extrema), Kepler-16b (circumbinario), YZ Ceti (3),
    # GJ 1061 (3), TOI-561 (sistema rocoso ~10 Gyr), K2-141 (mundo de lava),
    # GJ 49b, TOI-1231b, TOI-1266 (2). Mismas convenciones de honestidad de
    # dato que Lotes 1-3 (M/R estimados marcados explicitamente por planeta).
    # ========================================================================

    "HD_110067b": {"M": 1.368563e+25, "R_p": 1.235974e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.190763e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Cadena resonante de 6 subneptunos (Rice et al 2023), masa estimada [M estimada, a derivado via Kepler]", "estrella": "HD_110067", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_110067c": {"M": 1.787317e+25, "R_p": 1.357023e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.560493e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 110067, masa estimada [M estimada, a derivado via Kepler]", "estrella": "HD_110067", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_110067d": {"M": 4.107058e+25, "R_p": 1.815735e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.045456e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 110067, masa estimada [M estimada, a derivado via Kepler]", "estrella": "HD_110067", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_110067e": {"M": 1.835685e+25, "R_p": 1.369765e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.681147e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 110067, masa estimada [M estimada, a derivado via Kepler]", "estrella": "HD_110067", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_110067f": {"M": 3.124860e+25, "R_p": 1.650089e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.248014e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 110067, masa estimada [M estimada, a derivado via Kepler]", "estrella": "HD_110067", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_110067g": {"M": 1.536054e+25, "R_p": 1.286942e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.935934e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 110067, masa estimada [M estimada, a derivado via Kepler]", "estrella": "HD_110067", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "LHS_1140b": {"M": 4.168456e+25, "R_p": 1.100272e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.400236e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Candidato habitable rocoso/oceanico bien estudiado por JWST [todo real]", "estrella": "LHS_1140", "e_inicial": 0.0, "fuente_orbital": "real"},
    "LHS_1140c": {"M": 1.140652e+25, "R_p": 7.447699e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 4.001743e+09, "w_p_inicial": 1.929837e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Interior del sistema LHS 1140 [todo real]", "estrella": "LHS_1140", "e_inicial": 0.0, "fuente_orbital": "real"},
    "LHS_475b": {"M": 5.374800e+24, "R_p": 6.307290e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.184129e+09, "w_p_inicial": 3.581485e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Tamano casi-identico a la Tierra, confirmado por JWST 2023 [todo real]", "estrella": "LHS_475", "e_inicial": 0.0, "fuente_orbital": "real"},
    "LHS_3154b": {"M": 7.883040e+25, "R_p": 1.210490e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 3.500590e+09, "w_p_inicial": 1.965461e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Planeta anomalo, demasiado masivo para su estrella ultrafria [todo real]", "estrella": "LHS_3154", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_367b": {"M": 3.780276e+24, "R_p": 4.453329e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.047185e+09, "w_p_inicial": 2.272564e-04, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Planeta de hierro ultra-denso, periodo de 7.7 horas [todo real]", "estrella": "GJ_367", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_367c": {"M": 2.466436e+25, "R_p": 9.343597e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.002306e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema GJ 367, radio estimado (RV) [R estimado]", "estrella": "GJ_367", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_367d": {"M": 3.511536e+24, "R_p": 5.520005e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.004611e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema GJ 367, radio estimado (RV) [R estimado]", "estrella": "GJ_367", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "TOI_270b": {"M": 9.435760e+24, "R_p": 7.683426e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 4.861931e+09, "w_p_inicial": 2.164347e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Interior rocoso del sistema TOI-270 [todo real]", "estrella": "TOI_270", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_270c": {"M": 3.672780e+25, "R_p": 1.500370e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 6.791743e+09, "w_p_inicial": 1.284842e-05, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno del sistema TOI-270 [todo real]", "estrella": "TOI_270", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_270d": {"M": 2.854616e+25, "R_p": 1.358934e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.101040e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno exterior, estudiado por JWST (atmosfera) [todo real]", "estrella": "TOI_270", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_3470b": {"M": 7.512776e+25, "R_p": 2.911547e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 5.310724e+09, "w_p_inicial": 2.179526e-05, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno caliente, atmosfera estudiada extensamente [todo real]", "estrella": "GJ_3470", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_486b": {"M": 1.791600e+25, "R_p": 8.314155e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 2.588043e+09, "w_p_inicial": 4.957195e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Super-Tierra rocosa cercana, candidato a atmosfera [todo real]", "estrella": "GJ_486", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_357b": {"M": 1.098848e+25, "R_p": 7.753507e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 5.235925e+09, "w_p_inicial": 1.850434e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Interior del sistema GJ 357 [todo real]", "estrella": "GJ_357", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_357c": {"M": 2.030480e+25, "R_p": 8.865575e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 9.125470e+09, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema GJ 357, radio estimado (RV) [R estimado]", "estrella": "GJ_357", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_357d": {"M": 3.642920e+25, "R_p": 1.038118e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 3.051797e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Borde de zona habitable, radio estimado (RV) [R estimado]", "estrella": "GJ_357", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "WASP_18b": {"M": 1.935860e+28, "R_p": 8.320303e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.030853e+09, "w_p_inicial": 7.724473e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter muy masivo, periodo ultra-corto [todo real]", "estrella": "WASP_18", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_19b": {"M": 2.114262e+27, "R_p": 9.941512e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.471357e+09, "w_p_inicial": 9.218860e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter, uno de los periodos mas cortos conocidos [todo real]", "estrella": "WASP_19", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_43b": {"M": 3.894494e+27, "R_p": 7.398999e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.282864e+09, "w_p_inicial": 8.939624e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter, orbita muy cercana a estrella K [todo real]", "estrella": "WASP_43", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_76b": {"M": 1.746069e+27, "R_p": 1.306966e+08, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.936730e+09, "w_p_inicial": 4.018059e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter con lluvia de hierro en el lado nocturno [todo real]", "estrella": "WASP_76", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_121b": {"M": 2.195872e+27, "R_p": 1.331963e+08, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.805770e+09, "w_p_inicial": 5.704048e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter ultra-caliente, escape atmosferico detectado [todo real]", "estrella": "WASP_121", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_127b": {"M": 3.131538e+26, "R_p": 9.363019e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 7.240537e+09, "w_p_inicial": 1.740566e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Saturn de muy baja densidad [todo real]", "estrella": "WASP_127", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_6b": {"M": 9.546445e+26, "R_p": 8.741675e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.298070e+09, "w_p_inicial": 2.163696e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter tipico [todo real]", "estrella": "WASP_6", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_31b": {"M": 9.071970e+26, "R_p": 1.106279e+08, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.965277e+09, "w_p_inicial": 2.135191e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter de baja densidad [todo real]", "estrella": "WASP_31", "e_inicial": 0.0, "fuente_orbital": "real"},
    "WASP_96b": {"M": 9.109928e+26, "R_p": 8.570269e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.776784e+09, "w_p_inicial": 2.123148e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter, atmosfera de referencia para JWST [todo real]", "estrella": "WASP_96", "e_inicial": 0.0, "fuente_orbital": "real"},
    "HD_149026b": {"M": 6.813467e+26, "R_p": 5.127878e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.447668e+09, "w_p_inicial": 2.528601e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Saturn con nucleo solido masivo inferido [todo real]", "estrella": "HD_149026", "e_inicial": 0.0, "fuente_orbital": "real"},
    "HD_80606b": {"M": 7.971187e+27, "R_p": 6.791938e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.806703e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Excentricidad extrema (0.93), migracion por marea Kozai [todo real]", "estrella": "HD_80606", "e_inicial": 0.9336, "fuente_orbital": "real"},
    "HD_17156b": {"M": 6.056204e+27, "R_p": 7.927499e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.427973e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante de orbita excentrica y periodo intermedio [todo real]", "estrella": "HD_17156", "e_inicial": 0.6768, "fuente_orbital": "real"},
    "Kepler_16b": {"M": 6.320012e+26, "R_p": 5.383557e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.054366e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Planeta circumbinario (orbita 2 estrellas, tipo 'Tatooine') [todo real]", "estrella": "Kepler_16", "e_inicial": 0.0, "fuente_orbital": "real"},
    "YZ_Ceti_b": {"M": 4.479000e+24, "R_p": 5.894869e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.329239e+09, "w_p_inicial": 3.600102e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema ultra-compacto de 3 planetas, radio estimado (RV) [R estimado]", "estrella": "YZ_Ceti", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "YZ_Ceti_c": {"M": 5.852560e+24, "R_p": 6.336343e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 3.126595e+09, "w_p_inicial": 2.376538e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema YZ Ceti, radio estimado (RV) [R estimado]", "estrella": "YZ_Ceti", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "YZ_Ceti_d": {"M": 6.808080e+24, "R_p": 6.600425e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 4.265035e+09, "w_p_inicial": 1.560559e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema YZ Ceti, radio estimado (RV) [R estimado]", "estrella": "YZ_Ceti", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_1061b": {"M": 8.241360e+24, "R_p": 6.949842e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.827400e+09, "w_p_inicial": 2.269727e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema de 3 planetas en vecina cercana, radio estimado (RV) [R estimado]", "estrella": "GJ_1061", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_1061c": {"M": 1.045100e+25, "R_p": 7.410165e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 5.280805e+09, "w_p_inicial": 1.087189e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Posible zona habitable, radio estimado (RV) [R estimado]", "estrella": "GJ_1061", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_1061d": {"M": 1.003296e+25, "R_p": 7.328939e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 8.123164e+09, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Posible zona habitable exterior, radio estimado (RV) [R estimado]", "estrella": "GJ_1061", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "TOI_561b": {"M": 9.495480e+24, "R_p": 9.046820e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.690456e+09, "w_p_inicial": 1.628713e-04, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Uno de los sistemas rocosos mas antiguos conocidos (~10 Gyr) [todo real]", "estrella": "TOI_561", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_561c": {"M": 3.523480e+25, "R_p": 1.834848e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.383780e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema TOI-561, estrella de disco grueso [todo real]", "estrella": "TOI_561", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_561d": {"M": 6.569200e+25, "R_p": 1.478072e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.453405e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema TOI-561, estrella de disco grueso [todo real]", "estrella": "TOI_561", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_561e": {"M": 7.763600e+25, "R_p": 1.701057e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 5.131207e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema TOI-561, estrella de disco grueso [todo real]", "estrella": "TOI_561", "e_inicial": 0.0, "fuente_orbital": "real"},
    "K2_141b": {"M": 3.033776e+25, "R_p": 9.620210e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.121984e+09, "w_p_inicial": 2.594066e-04, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Mundo de lava, periodo de 6.7 horas, oceano de magma dayside [todo real]", "estrella": "K2_141", "e_inicial": 0.0, "fuente_orbital": "real"},
    "K2_141c": {"M": 4.598440e+25, "R_p": 1.105503e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 9.649063e+09, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema K2-141, radio estimado (RV) [R estimado]", "estrella": "K2_141", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_49b": {"M": 2.388800e+25, "R_p": 1.178635e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.346381e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno templado transitante [todo real]", "estrella": "GJ_49", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_1231b": {"M": 9.196880e+25, "R_p": 2.325415e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.487003e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "SubNeptuno templado, atmosfera estudiada por HST [todo real]", "estrella": "TOI_1231", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_1266b": {"M": 5.374800e+25, "R_p": 1.509927e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.095056e+10, "w_p_inicial": 6.674810e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Interior del sistema TOI-1266 [todo real]", "estrella": "TOI_1266", "e_inicial": 0.0, "fuente_orbital": "real"},
    "TOI_1266c": {"M": 2.388800e+25, "R_p": 9.938760e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.581249e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Exterior del sistema TOI-1266 [todo real]", "estrella": "TOI_1266", "e_inicial": 0.0, "fuente_orbital": "real"},

    # ========================================================================
    # LOTE 5 (v5.8) -- 68 exoplanetas: sistemas Kepler multi-planeta
    # (Kepler-9/10/36/37/42/444/80/102/138), singles RV/transito cercanos
    # (GJ 15A/176/179/3512, Ross 128), HD 40307 (b-f), 61 Virginis, HR 858,
    # 5 candidatos de zona habitable (Kepler-1544/1652/1638/1606/1090),
    # gigantes RV clasicos (tau Bootis, Upsilon Andromedae, 47 UMa,
    # HD 69830, GJ 581, 14 Herculis). Mismas convenciones de honestidad
    # de dato que Lotes 1-4.
    # ========================================================================

    "Kepler_9b": {"M": 4.782712e+26, "R_p": 6.013472e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.094370e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Par de gigantes en resonancia 2:1, primer sistema multi-transito confirmado [todo real]", "estrella": "Kepler_9", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_9c": {"M": 3.245412e+26, "R_p": 5.877776e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.365952e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Sistema Kepler-9, segundo gigante en resonancia [todo real]", "estrella": "Kepler_9", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_9d": {"M": 4.180400e+25, "R_p": 1.044844e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 4.084022e+09, "w_p_inicial": 4.565101e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Interior rocoso del sistema Kepler-9 [todo real]", "estrella": "Kepler_9", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_10b": {"M": 2.221584e+25, "R_p": 9.365370e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 2.513244e+09, "w_p_inicial": 8.688417e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "El primer rocoso confirmado por Kepler (2011) [todo real]", "estrella": "Kepler_10", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_10c": {"M": 1.027184e+26, "R_p": 1.497185e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.590349e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-10, 'mega-Tierra' densa [todo real]", "estrella": "Kepler_10", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_36b": {"M": 2.657540e+25, "R_p": 9.429080e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.724863e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Par de vecinos con contraste extremo de densidad [todo real]", "estrella": "Kepler_36", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_36c": {"M": 4.825376e+25, "R_p": 2.344528e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.919341e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Par de vecinos con contraste extremo de densidad [todo real]", "estrella": "Kepler_36", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_37b": {"M": 8.814034e+22, "R_p": 2.038720e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.506451e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Mas pequeno que Mercurio, uno de los exoplanetas mas chicos conocidos [M estimada]", "estrella": "Kepler_37", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_37c": {"M": 2.059902e+24, "R_p": 4.778250e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.167673e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-37 [M estimada]", "estrella": "Kepler_37", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_37d": {"M": 1.368563e+25, "R_p": 1.235974e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.152027e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-37 [M estimada]", "estrella": "Kepler_37", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_42b": {"M": 2.381606e+24, "R_p": 4.969380e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.735335e+09, "w_p_inicial": 5.990284e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema ultra-compacto de enana M, 3 planetas menores a la Tierra [M estimada]", "estrella": "Kepler_42", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_42c": {"M": 1.863865e+24, "R_p": 4.650830e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 8.975872e+08, "w_p_inicial": 1.605343e-04, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-42 [M estimada]", "estrella": "Kepler_42", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_42d": {"M": 7.462026e+23, "R_p": 3.631470e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.303807e+09, "w_p_inicial": 3.899306e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-42 [M estimada]", "estrella": "Kepler_42", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_444b": {"M": 2.068943e+23, "R_p": 2.567513e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 6.118553e+09, "w_p_inicial": 2.020057e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema de 11000 millones de anos, 5 sub-Tierras [M estimada]", "estrella": "Kepler_444", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_444c": {"M": 4.494056e+23, "R_p": 3.166387e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 7.315336e+09, "w_p_inicial": 1.599693e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-444, uno de los mas antiguos conocidos [M estimada]", "estrella": "Kepler_444", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_444d": {"M": 5.700862e+23, "R_p": 3.376630e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 9.005792e+09, "w_p_inicial": 1.175021e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-444 [M estimada]", "estrella": "Kepler_444", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_444e": {"M": 6.364035e+23, "R_p": 3.478566e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.036713e+10, "w_p_inicial": 9.391974e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-444 [M estimada]", "estrella": "Kepler_444", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_444f": {"M": 1.969914e+24, "R_p": 4.720911e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.213239e+10, "w_p_inicial": 7.466330e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-444 [M estimada]", "estrella": "Kepler_444", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_80b": {"M": 4.031100e+25, "R_p": 1.293313e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 9.050671e+09, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Cadena resonante de 6 planetas, similar a TRAPPIST-1 [todo real]", "estrella": "Kepler_80", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_80c": {"M": 2.597820e+25, "R_p": 1.726541e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.107024e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-80 [todo real]", "estrella": "Kepler_80", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_80d": {"M": 3.941520e+24, "R_p": 8.154880e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 5.101287e+09, "w_p_inicial": 2.368796e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-80 [todo real]", "estrella": "Kepler_80", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_80e": {"M": 4.060960e+24, "R_p": 7.199230e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 6.806703e+09, "w_p_inicial": 1.563915e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Sistema Kepler-80 [todo real]", "estrella": "Kepler_80", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_80f": {"M": 1.618412e+25, "R_p": 1.401620e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.487003e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema Kepler-80 [todo real]", "estrella": "Kepler_80", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_80g": {"M": 5.972000e+24, "R_p": 7.199230e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.243968e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Exterior del sistema Kepler-80, menos establecido [todo real]", "estrella": "Kepler_80", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_102b": {"M": 3.654954e+23, "R_p": 2.994370e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 8.272762e+09, "w_p_inicial": 1.375488e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_102", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_102c": {"M": 7.957990e+23, "R_p": 3.695180e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 9.933299e+09, "w_p_inicial": 1.028455e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_102", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_102d": {"M": 1.101750e+25, "R_p": 7.517780e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.279062e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_102", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_102e": {"M": 5.332996e+25, "R_p": 1.414362e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.715888e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Planeta denso y anomalo del sistema Kepler-102 (masa medida) [todo real]", "estrella": "Kepler_102", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_102f": {"M": 3.721394e+24, "R_p": 5.606480e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 2.477341e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_102", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_138b": {"M": 3.941520e+23, "R_p": 3.325662e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.110016e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 5 v5.8 [todo real]", "estrella": "Kepler_138", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_138c": {"M": 1.373560e+25, "R_p": 7.645200e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.365829e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 5 v5.8 [todo real]", "estrella": "Kepler_138", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_138d": {"M": 1.254120e+25, "R_p": 9.620210e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.920837e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Candidato a 'mundo de agua' - densidad sorprendentemente baja [todo real]", "estrella": "Kepler_138", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_15Ab": {"M": 1.809516e+25, "R_p": 8.594035e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.078601e+10, "w_p_inicial": 6.356823e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "GJ_15A", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_176b": {"M": 4.956760e+25, "R_p": 1.128129e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 9.873459e+09, "w_p_inicial": 8.285808e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "GJ_176", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_179b": {"M": 1.563871e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.605309e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante RV de periodo largo [R estimado]", "estrella": "GJ_179", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_3512b": {"M": 8.730347e+26, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 5.022001e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante inusualmente masivo para su estrella M enana [R estimado]", "estrella": "GJ_3512", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Ross_128b": {"M": 8.062200e+24, "R_p": 6.908722e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 7.420054e+09, "w_p_inicial": 7.371126e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Vecina cercana muy tranquila (baja actividad estelar) [R estimado]", "estrella": "Ross_128", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_40307b": {"M": 2.388800e+25, "R_p": 9.263259e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 7.001180e+09, "w_p_inicial": 1.686387e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "HD_40307", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_40307c": {"M": 3.822080e+25, "R_p": 1.051662e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.195287e+10, "w_p_inicial": 7.560722e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "HD_40307", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_40307d": {"M": 5.553960e+25, "R_p": 1.163317e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.992644e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "HD_40307", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_40307e": {"M": 2.090200e+25, "R_p": 8.935235e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 2.836376e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "HD_40307", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_40307f": {"M": 3.105440e+25, "R_p": 9.943253e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 3.695067e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "HD_40307", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Vir61_b": {"M": 3.045720e+25, "R_p": 9.891259e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 7.479894e+09, "w_p_inicial": 1.725316e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "Vir61", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Vir61_c": {"M": 1.086904e+26, "R_p": 1.849973e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.261234e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "Vir61", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Vir61_d": {"M": 1.367588e+26, "R_p": 1.959325e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 7.120859e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [R estimado]", "estrella": "Vir61", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HR_858b": {"M": 1.681534e+25, "R_p": 1.328354e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 6.731904e+09, "w_p_inicial": 2.028509e-05, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "HR_858", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HR_858c": {"M": 1.366548e+25, "R_p": 1.235337e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 9.574264e+09, "w_p_inicial": 1.217513e-05, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "HR_858", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HR_858d": {"M": 1.870045e+25, "R_p": 1.378684e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.466059e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "HR_858", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_1544b": {"M": 2.743687e+25, "R_p": 9.620210e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 8.212923e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_1544", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_1652b": {"M": 1.019456e+25, "R_p": 1.114925e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.902199e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_1652", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_1638b": {"M": 1.140342e+25, "R_p": 1.159522e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.113008e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_1638", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_1606b": {"M": 9.072248e+24, "R_p": 1.070328e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 9.275068e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_1606", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_1090b": {"M": 1.787317e+25, "R_p": 1.357023e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 9.230189e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 5 v5.8 [M estimada]", "estrella": "Kepler_1090", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "tauBoo_b": {"M": 1.129251e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.911422e+09, "w_p_inicial": 2.365329e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Primer planeta con deteccion directa de CO en su atmosfera [R estimado]", "estrella": "tauBoo", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "UpsAnd_b": {"M": 1.309552e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 8.901073e+09, "w_p_inicial": 1.575093e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Sistema Upsilon Andromedae, hot Jupiter interior [R estimado]", "estrella": "UpsAnd", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "UpsAnd_c": {"M": 2.653266e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.238670e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Sistema Upsilon Andromedae, masa real via astrometria [R estimado]", "estrella": "UpsAnd", "e_inicial": 0.245, "fuente_orbital": "estimado"},
    "UpsAnd_d": {"M": 1.945349e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.784826e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Sistema Upsilon Andromedae, masa real via astrometria [R estimado]", "estrella": "UpsAnd", "e_inicial": 0.316, "fuente_orbital": "estimado"},
    "UMa47_b": {"M": 4.801691e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.141555e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Uno de los primeros analogos de Jupiter descubiertos (1996) [R estimado]", "estrella": "UMa47", "e_inicial": 0.032, "fuente_orbital": "estimado"},
    "UMa47_c": {"M": 1.024867e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 5.385523e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Sistema 47 Ursae Majoris [R estimado]", "estrella": "UMa47", "e_inicial": 0.098, "fuente_orbital": "estimado"},
    "UMa47_d": {"M": 3.112559e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.735335e+12, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante de periodo muy largo (~38 anios) [R estimado]", "estrella": "UMa47", "e_inicial": 0.16, "fuente_orbital": "estimado"},
    "HD_69830b": {"M": 6.091440e+25, "R_p": 1.600655e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.174343e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Trio de Neptunos sin transito, disco de escombros conocido [R estimado]", "estrella": "HD_69830", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_69830c": {"M": 7.046960e+25, "R_p": 1.660038e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.782520e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 69830 [R estimado]", "estrella": "HD_69830", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_69830d": {"M": 1.080932e+26, "R_p": 1.847427e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 9.424666e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema HD 69830 [R estimado]", "estrella": "HD_69830", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_581b": {"M": 9.435760e+25, "R_p": 1.785714e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 6.073674e+09, "w_p_inicial": 1.354556e-05, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema GJ 581, historicamente disputado (b,d,e solidos; c,f,g retractados) [R estimado]", "estrella": "GJ_581", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_581d": {"M": 3.344320e+25, "R_p": 1.014421e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 3.261234e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Borde de zona habitable, sistema historicamente disputado [R estimado]", "estrella": "GJ_581", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_581e": {"M": 1.015240e+25, "R_p": 7.352395e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 4.263539e+09, "w_p_inicial": 2.309370e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "El mas liviano del sistema GJ 581 [R estimado]", "estrella": "GJ_581", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Her14_b": {"M": 1.527811e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.383218e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante de orbita excentrica, conocido desde 2002 [R estimado]", "estrella": "Her14", "e_inicial": 0.369, "fuente_orbital": "estimado"},
    "Her14_c": {"M": 1.309552e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.346381e+12, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Companero exterior de periodo muy largo [R estimado]", "estrella": "Her14", "e_inicial": 0.35, "fuente_orbital": "estimado"},

    # ========================================================================
    # LOTE 6 (v5.9) -- 50 exoplanetas: mayoria gigantes RV clasicos de
    # sistemas multi-planeta de larga trayectoria observacional (HD 190360,
    # 128311, 108874, 74156, 183263, 187123, 12661, 217107, 168443, 27894,
    # 37124), 82 G. Eridani b/c (mismo sistema que G82_Eridani_d ya en
    # base), 16 Cygni B b, Kepler-56/419/448, sistema GJ 1148/3323/686/96/
    # 625/229A, 24 Sextantis, y 6 candidatos de zona habitable Kepler
    # (296e/440b/61b/298d/1410b/1229b). Mismas convenciones de honestidad
    # de dato que lotes anteriores.
    # ========================================================================

    "G82_Eridani_b": {"M": 1.558692e+25, "R_p": 8.254686e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.805646e+10, "w_p_inicial": 3.969544e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema 82 G. Eridani, interior de G82_Eridani_d (ya en base) [R estimado]", "estrella": "G82_Eridani", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "G82_Eridani_c": {"M": 2.287276e+25, "R_p": 9.155272e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 3.099668e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Sistema 82 G. Eridani [R estimado]", "estrella": "G82_Eridani", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_216435b": {"M": 2.391356e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.829705e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_216435", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_154345b": {"M": 1.804904e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.268151e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_154345", "e_inicial": 0.044, "fuente_orbital": "estimado"},
    "HD_190360b": {"M": 2.850648e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 5.968955e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_190360", "e_inicial": 0.31, "fuente_orbital": "estimado"},
    "HD_190360c": {"M": 1.113778e+26, "R_p": 1.861304e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.914853e+10, "w_p_inicial": 4.252752e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_190360", "e_inicial": 0.005, "fuente_orbital": "estimado"},
    "HD_128311b": {"M": 4.137425e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.645577e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_128311", "e_inicial": 0.35, "fuente_orbital": "estimado"},
    "HD_128311c": {"M": 6.092264e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.632923e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_128311", "e_inicial": 0.17, "fuente_orbital": "estimado"},
    "HD_108874b": {"M": 2.581146e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.572274e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_108874", "e_inicial": 0.07, "fuente_orbital": "estimado"},
    "HD_108874c": {"M": 1.932064e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.009223e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_108874", "e_inicial": 0.25, "fuente_orbital": "estimado"},
    "HD_74156b": {"M": 3.530097e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.398177e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_74156", "e_inicial": 0.64, "fuente_orbital": "estimado"},
    "HD_74156c": {"M": 1.524015e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 5.759518e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_74156", "e_inicial": 0.4, "fuente_orbital": "estimado"},
    "HD_183263b": {"M": 7.003257e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.273888e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_183263", "e_inicial": 0.36, "fuente_orbital": "estimado"},
    "HD_183263c": {"M": 6.775509e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.507507e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_183263", "e_inicial": 0.239, "fuente_orbital": "estimado"},
    "HD_187123b": {"M": 9.926025e+26, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 6.372869e+09, "w_p_inicial": 2.348145e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_187123", "e_inicial": 0.01, "fuente_orbital": "estimado"},
    "HD_187123c": {"M": 3.776824e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 7.315336e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_187123", "e_inicial": 0.252, "fuente_orbital": "estimado"},
    "HD_12661b": {"M": 4.365174e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.243158e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_12661", "e_inicial": 0.35, "fuente_orbital": "estimado"},
    "HD_12661c": {"M": 3.643971e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.338338e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_12661", "e_inicial": 0.031, "fuente_orbital": "estimado"},
    "HD_217107b": {"M": 2.638083e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.118992e+10, "w_p_inicial": 1.020388e-05, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_217107", "e_inicial": 0.129, "fuente_orbital": "estimado"},
    "HD_217107c": {"M": 4.934544e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 7.958607e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_217107", "e_inicial": 0.4, "fuente_orbital": "estimado"},
    "HD_168443b": {"M": 1.453603e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.384714e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_168443", "e_inicial": 0.529, "fuente_orbital": "estimado"},
    "HD_168443c": {"M": 3.262493e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.256059e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Masa cercana al limite de enana marron (17 M_Jup) [R estimado]", "estrella": "HD_168443", "e_inicial": 0.2113, "fuente_orbital": "estimado"},
    "Cyg16B_b": {"M": 3.188475e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.483325e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "Cyg16B", "e_inicial": 0.68, "fuente_orbital": "estimado"},
    "Kepler_56b": {"M": 1.319812e+26, "R_p": 5.141397e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.537866e+10, "w_p_inicial": 6.925910e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Orbita desalineada con el ecuador de su estrella subgigante [todo real]", "estrella": "Kepler_56", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_56c": {"M": 1.080932e+27, "R_p": 5.644706e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.471357e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Sistema Kepler-56, orbita desalineada [todo real]", "estrella": "Kepler_56", "e_inicial": 0.0, "fuente_orbital": "real"},
    "Kepler_419b": {"M": 4.744754e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 5.535121e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Par de gigantes de alta excentricidad [R estimado]", "estrella": "Kepler_419", "e_inicial": 0.83, "fuente_orbital": "estimado"},
    "Kepler_419c": {"M": 1.385468e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.263539e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Sistema Kepler-419 [R estimado]", "estrella": "Kepler_419", "e_inicial": 0.184, "fuente_orbital": "estimado"},
    "Kepler_448b": {"M": 1.613216e+27, "R_p": 1.251259e+08, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.318767e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Hot Jupiter inflado con orbita muy inclinada [todo real]", "estrella": "Kepler_448", "e_inicial": 0.0, "fuente_orbital": "real"},
    "GJ_1148b": {"M": 5.249388e+26, "R_p": 2.742489e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 2.483325e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Par de Neptunos RV alrededor de enana M activa [R estimado]", "estrella": "GJ_1148", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_1148c": {"M": 4.060960e+26, "R_p": 2.572023e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 1.395748e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Sistema GJ 1148 [R estimado]", "estrella": "GJ_1148", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_3323b": {"M": 1.206344e+25, "R_p": 7.702868e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 4.936730e+09, "w_p_inicial": 1.356755e-05, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "GJ_3323", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_3323c": {"M": 8.599680e+24, "R_p": 7.030164e+06, "inercia": 0.33, "densidad_nucleo": 10000.0, "difusividad": 1.2, "a_inicial": 1.002306e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Terrestre", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "GJ_3323", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_686b": {"M": 4.234148e+25, "R_p": 1.081140e+07, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.383780e+10, "w_p_inicial": 4.682682e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "GJ_686", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_96b": {"M": 1.039128e+26, "R_p": 1.829300e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 4.398177e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "GJ_96", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_625b": {"M": 1.684104e+25, "R_p": 8.428977e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 1.172847e+10, "w_p_inicial": 4.971428e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "GJ_625", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "GJ_229Ab": {"M": 1.499342e+28, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 5.056408e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Gigante inusualmente masivo, sistema con la enana marron GJ 229B [R estimado]", "estrella": "GJ_229A", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Sex24_b": {"M": 3.776824e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.994140e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "Sex24", "e_inicial": 0.09, "fuente_orbital": "estimado"},
    "Sex24_c": {"M": 1.632195e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 3.111636e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "Sex24", "e_inicial": 0.29, "fuente_orbital": "estimado"},
    "HD_27894b": {"M": 1.176699e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 1.869973e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_27894", "e_inicial": 0.05, "fuente_orbital": "estimado"},
    "HD_27894c": {"M": 8.539960e+25, "R_p": 1.741733e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 9.409706e+09, "w_p_inicial": 1.374708e-05, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_27894", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "HD_27894d": {"M": 1.176699e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 8.227883e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_27894", "e_inicial": 0.32, "fuente_orbital": "estimado"},
    "HD_37124b": {"M": 1.281084e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 7.913727e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_37124", "e_inicial": 0.054, "fuente_orbital": "estimado"},
    "HD_37124c": {"M": 1.237432e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 2.558124e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_37124", "e_inicial": 0.14, "fuente_orbital": "estimado"},
    "HD_37124d": {"M": 1.320940e+27, "R_p": 6.991100e+07, "inercia": 0.25, "densidad_nucleo": 11000.0, "difusividad": 2.3, "a_inicial": 4.772172e+11, "w_p_inicial": 7.000000e-06, "B_p_inicial": 4.00e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "Gigante gaseoso", "descripcion": "Lote 6 v5.9 [R estimado]", "estrella": "HD_37124", "e_inicial": 0.2, "fuente_orbital": "estimado"},
    "Kepler_296e": {"M": 2.880568e+25, "R_p": 9.747630e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 2.528204e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Candidato en zona habitable, sistema binario de enanas M [M estimada]", "estrella": "Kepler_296", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_440b": {"M": 1.213420e+25, "R_p": 1.185006e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 5.235925e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Zona habitable, radio y masa consistentes con super-Tierra [M estimada]", "estrella": "Kepler_440", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_61b": {"M": 1.835685e+25, "R_p": 1.369765e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 3.889545e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Zona habitable de estrella K [M estimada]", "estrella": "Kepler_61", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_298d": {"M": 2.824526e+25, "R_p": 1.592750e+07, "inercia": 0.3, "densidad_nucleo": 7200.0, "difusividad": 1.8, "a_inicial": 4.817051e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.20e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "Zona habitable, sistema con 4 planetas [M estimada]", "estrella": "Kepler_298", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_1410b": {"M": 2.019643e+25, "R_p": 8.855690e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 4.338338e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Zona habitable de estrella tipo Sol [M estimada]", "estrella": "Kepler_1410", "e_inicial": 0.0, "fuente_orbital": "estimado"},
    "Kepler_1229b": {"M": 2.073927e+25, "R_p": 8.919400e+06, "inercia": 0.32, "densidad_nucleo": 8200.0, "difusividad": 1.7, "a_inicial": 4.502896e+10, "w_p_inicial": 7.000000e-06, "B_p_inicial": 1.10e-04, "rho_sw": 1.0e-18, "v_sw": 3.5e5, "w_estrella": 3.0e-6, "tipo_planeta": "SuperTierra", "descripcion": "Zona habitable de enana M [M estimada]", "estrella": "Kepler_1229", "e_inicial": 0.0, "fuente_orbital": "estimado"},

}

# ============================================================================
# NUEVO v5.2: parámetros térmicos estimados para exoplanetas sin dato real
# ----------------------------------------------------------------------------
# Solo Venus, Tierra, Marte y Júpiter (arriba) tienen R_core/T_cmb_inicial_K/
# T_manto_inicial_K/Q_cmb_hoy_W/k_manto/regimen_tectonico/albedo puestos a
# mano, calibrados o tomados de datos reales. Los 43 planetas restantes no
# tenían estos campos: si alguien activaba el modelo térmico sobre ellos,
# el motor corría con los defaults genéricos de termica.py/engine.py
# (iguales para cualquier planeta), no con nada derivado de sus propios
# M/R_p/tipo_planeta.
#
# Lo de abajo NO es un ajuste físico nuevo -- es una tabla de valores por
# categoría de planeta, con una advertencia honesta sobre qué tan sólido es
# cada campo:
#
#   - ratio_core (R_core/R_p): SÓLIDO para terrestres. Venus/Tierra/Marte
#     dan 0.529/0.547/0.540 -- consistente, se promedia a 0.54. Para
#     gigantes se reutiliza el ratio de Júpiter (0.143), que en el propio
#     bloque de Júpiter arriba ya está documentado como valor de
#     calibración, no un núcleo físico real -- para SubNeptuno/Gigante de
#     hielo es una extrapolación todavía más floja, marcada igual.
#
#   - k_manto y albedo: DERIVABLE por categoría. Rango angosto en los 4
#     casos reales (k_manto 2.5-3.5); el albedo de Venus/Tierra/Marte/
#     Júpiter arriba coincide con el albedo de Bond real de cada uno, así
#     que para los gigantes se usan valores de la literatura (Urano/Neptuno
#     ~0.3, hot Jupiters muy irradiados ~0.1 por atmósferas absorbentes)
#     en vez de inventar un número.
#
#   - regimen_tectonico: NO ES DERIVABLE. Ni con datos reales de la Tierra
#     sabemos el régimen tectónico de un exoplaneta sin observación directa
#     (no existe tal observación para ninguno de estos 43). Es un supuesto
#     de diseño, no un dato reconstruido -- ver flag
#     'regimen_tectonico_conocido' más abajo, mismo patron que
#     'eps_conocido' para oblicuidad.
#
#   - T_cmb_inicial_K / T_manto_inicial_K: el MENOS limpio de todos. En los
#     4 casos reales, Venus (menos masivo que la Tierra) tiene T_cmb MAYOR
#     que la Tierra -- no hay una relación monótona con la masa en los
#     propios datos de calibración. En vez de fingir una ley física con una
#     curva ajustada a 4 puntos, se usa un valor de referencia por
#     categoría (parecido al cuerpo real más representativo) con una
#     variación suave y declaradamente heurística según la masa relativa
#     dentro de la categoría -- exponente 0.15, elegido solo para introducir
#     variación entre planetas de la misma categoría, no una ley ajustada.
#
#   - Q_cmb_hoy_W: no se usa en ningún cálculo del motor (ni en termica.py
#     ni en engine.py) -- queda solo por consistencia de esquema con los 4
#     bloques reales, no afecta ningún resultado.
# ============================================================================

_M_TIERRA = 5.972e24
_M_JUPITER = 1.898e27

CATEGORIAS_TERMICAS = {
    "Terrestre":        dict(ratio_core=0.54,  k_manto=3.0, albedo=0.30, regimen_tectonico=1,
                              T_cmb_ref=4000.0, T_manto_ref=2000.0, Q_cmb_ref=4.5e12, M_ref=_M_TIERRA),
    "SuperTierra":       dict(ratio_core=0.54,  k_manto=3.0, albedo=0.30, regimen_tectonico=1,
                              T_cmb_ref=4200.0, T_manto_ref=2100.0, Q_cmb_ref=6.0e12, M_ref=_M_TIERRA),
    "SubNeptuno":        dict(ratio_core=0.30,  k_manto=2.5, albedo=0.35, regimen_tectonico=0,
                              T_cmb_ref=6000.0, T_manto_ref=3200.0, Q_cmb_ref=1.5e13, M_ref=6.0 * _M_TIERRA),
    "Gigante gaseoso":   dict(ratio_core=0.143, k_manto=3.0, albedo=0.50, regimen_tectonico=1,
                              T_cmb_ref=15000.0, T_manto_ref=10000.0, Q_cmb_ref=1.0e14, M_ref=_M_JUPITER),
    "Gigante de hielo":  dict(ratio_core=0.20,  k_manto=2.5, albedo=0.30, regimen_tectonico=0,
                              T_cmb_ref=7000.0, T_manto_ref=4000.0, Q_cmb_ref=2.0e13, M_ref=0.05 * _M_JUPITER),
    "Hot Jupiter":       dict(ratio_core=0.143, k_manto=3.0, albedo=0.10, regimen_tectonico=1,
                              T_cmb_ref=15000.0, T_manto_ref=10000.0, Q_cmb_ref=1.0e14, M_ref=_M_JUPITER),
}


def _estimar_parametros_termicos(tipo_planeta: str, M: float, R_p: float) -> dict:
    """Estima R_core/T_cmb/T_manto/Q_cmb/k_manto/regimen_tectonico/albedo
    para un planeta sin datos térmicos reales, a partir de su categoría y
    masa. Ver nota extensa arriba: k_manto/albedo/ratio_core son derivados
    con distintos grados de confianza; regimen_tectonico es un supuesto de
    diseño, no un dato; T_cmb/T_manto son heurísticos, no una ley física
    ajustada. Devuelve también 'termico_estimado': True y
    'regimen_tectonico_conocido': False para que la UI/documentación puedan
    distinguir estos valores de los 4 casos calibrados con datos reales.
    """
    cat = CATEGORIAS_TERMICAS.get(tipo_planeta, CATEGORIAS_TERMICAS["Terrestre"])
    factor_masa = float(np.clip((M / cat["M_ref"]) ** 0.15, 0.5, 2.0))
    return {
        "R_core": cat["ratio_core"] * R_p,
        "T_cmb_inicial_K": cat["T_cmb_ref"] * factor_masa,
        "T_manto_inicial_K": cat["T_manto_ref"] * factor_masa,
        "Q_cmb_hoy_W": cat["Q_cmb_ref"] * factor_masa,
        "k_manto": cat["k_manto"],
        "regimen_tectonico": cat["regimen_tectonico"],
        "albedo": cat["albedo"],
        "termico_estimado": True,
        "regimen_tectonico_conocido": False,
    }


for nombre, datos in PLANETAS.items():
    if "e_inicial" not in datos:
        datos["e_inicial"] = E_INICIAL_SISTEMA_SOLAR.get(nombre, 0.0)
    # NUEVO v5.1 (oblicuidad, fix A.5 del informe de revision): distinguimos
    # "no tenemos el dato" de "sabemos que es bajo". Solo 5 cuerpos (Tierra,
    # Marte, Jupiter, Urano, Venus) tienen eps_inicial_deg real puesto arriba,
    # con eps_conocido=True. Para el resto (incluidos los ~39 exoplanetas),
    # dejamos eps_inicial_deg=0.0 (retrocompatibilidad numerica: el motor no
    # crashea) pero eps_conocido=False, para que habitabilidad.py NO aplique
    # la penalizacion por oblicuidad extrema cuando el dato es desconocido en
    # vez de realmente bajo.
    if "eps_inicial_deg" not in datos:
        datos["eps_inicial_deg"] = 0.0
        datos["eps_conocido"] = False
    # NUEVO v5.2: parametros termicos. Los 4 cuerpos con datos reales
    # (Venus/Tierra/Marte/Jupiter) ya traen "R_core" puesto arriba -- se
    # marcan explicitamente como no-estimados/conocidos para que la UI y la
    # documentacion puedan distinguirlos sin ambiguedad. El resto recibe la
    # estimacion por categoria de _estimar_parametros_termicos().
    if "R_core" not in datos:
        datos.update(_estimar_parametros_termicos(
            datos.get("tipo_planeta", "Terrestre"), datos["M"], datos["R_p"]
        ))
    else:
        datos.setdefault("termico_estimado", False)
        datos.setdefault("regimen_tectonico_conocido", True)

# ============================================================================
# NUEVO v5.4: esquema de tiers de confianza para escalar la base a 1000
# exoplanetas sin perder trazabilidad de qué dato es real y cuál estimado.
# ----------------------------------------------------------------------------
# fuente_orbital: "real" | "estimado" -- indica si M/R_p/a_inicial vienen de
# una fuente publicada (paper de descubrimiento, NASA Exoplanet Archive) o
# fueron estimados por plausibilidad. Hasta v5.3 este dato no se rastreaba
# en ningun lado.
#
# _FUENTE_ORBITAL_REAL_CONOCIDA es una lista explícita (no derivada de
# PLANETAS.keys() en tiempo de carga) de los 47 planetas que YA estaban en
# la base antes de v5.4, todos con M/R_p tomados de sus papers de
# descubrimiento o catálogos oficiales. Cualquier planeta agregado DESPUÉS
# de v5.4 sin declarar fuente_orbital explícitamente cae en default
# "revisar_pendiente" (ver setdefault abajo) -- fuerza declarar el origen
# del dato en vez de asumir "real" por omisión.
# ============================================================================
_FUENTE_ORBITAL_REAL_CONOCIDA = {
    "Mercurio", "Venus", "Tierra", "Marte", "Jupiter", "Saturno", "Urano", "Neptuno",
    "Proxima_b", "GJ_1132b", "WASP_12b", "TRAPPIST_1e", "Kepler_442b", "Kepler_452b",
    "GJ_581c", "HD_209458b", "HD_189733b", "Barnard_b", "GJ_273b", "Teegarden_b",
    "Teegarden_c", "Luyten_b", "Wolf_1061c", "Gliese_667Cc", "Gliese_832c",
    "Kepler_186f", "Kepler_62f", "Kepler_69c", "Kepler_22b", "Kepler_1649c",
    "TOI_700d", "Tau_Ceti_e", "GJ_180_b", "GJ_422_b", "K2_18b", "K2_18c",
    "HD_40307g", "HD_85512b", "GJ_1214b", "55_Cancri_e", "WASP_17b", "WASP_39b",
    "CoRoT_7b", "EPIC_201912552b", "K2_3d", "HD_219134b", "GJ_3293b",
}

for nombre, datos in PLANETAS.items():
    if nombre in _FUENTE_ORBITAL_REAL_CONOCIDA:
        datos.setdefault("fuente_orbital", "real")
    else:
        datos.setdefault("fuente_orbital", "revisar_pendiente")


def calcular_tier(datos: dict) -> str:
    """Calcula el tier de confianza de un planeta a partir de flags YA
    existentes en su dict -- no requiere etiquetar cada planeta a mano.

    Tier A: fuente_orbital real Y parametros termicos NO estimados
            (los 4 cuerpos calibrados: Venus/Tierra/Marte/Jupiter -- mas
            Urano/Neptuno, que tienen fuente_orbital real pero SI reciben
            termico estimado por categoria, por lo que caen en Tier B).
    Tier B: fuente_orbital real pero parametros termicos estimados por
            categoria (la mayoria de los exoplanetas actuales).
    Tier C: fuente_orbital estimado o sin declarar (planetas nuevos sin
            fuente confirmada).
    """
    fuente = datos.get("fuente_orbital", "revisar_pendiente")
    if fuente != "real":
        return "C"
    if not datos.get("termico_estimado", True):
        return "A"
    return "B"


LUNAS = {
    "Tierra": {"masa": 7.342e22, "a_luna_inicial": 3.844e8, "k2": 0.3, "Q_p": 12},
}
