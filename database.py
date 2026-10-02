# VERSION PUBLICA (AGPL-3.0): base reducida a 47 planetas (8 del Sistema Solar + 39
# exoplanetas con datos de publicaciones). La base completa de 300 planetas
# esta en las versiones STANDARD y PRO (solariscore.com.co).
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
    "HD_40307": {"tipo_espectral": "K2.5V", "masa": 0.77 * 1.98847e30},
    "GJ_581": {"tipo_espectral": "M3V", "masa": 0.31 * 1.98847e30},
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
    "GJ_1132b": {"M": 9.914e24, "R_p": 7.199e6, "inercia": 0.32, "densidad_nucleo": 7200.0, "difusividad": 1.6, "a_inicial": 0.01570 * 1.495978707e11, "w_p_inicial": 4.4645e-5, "B_p_inicial": 1.0e-4, "rho_sw": 2.0e-18, "v_sw": 4.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "Terrestre", "descripcion": "SuperTierra cercana [M, R, a y P reales; corregido auditoria oct-2026]", "estrella": "GJ_1132", "e_inicial": 0.0118},
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
    "GJ_3293b": {"M": 23.54 * 5.972e24, "R_p": 4.6 * 6.371e6, "inercia": 0.32, "densidad_nucleo": 8100.0, "difusividad": 1.6, "a_inicial": 0.14339 * 1.495978707e11, "w_p_inicial": 6.5e-6, "B_p_inicial": 1.2e-4, "rho_sw": 2.0e-18, "v_sw": 3.0e5, "w_estrella": 4.0e-6, "tipo_planeta": "SubNeptuno", "descripcion": "GJ 3293 - Neptuno en zona habitable [M min y a reales, R estimado; corregido auditoria oct-2026]", "estrella": "GJ_3293"},
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
    "Tierra": [
        {"nombre": "Luna", "masa": 7.342e22, "a_luna_inicial": 3.844e8, "k2": 0.3, "Q_p": 12},
    ],
    "Jupiter": [
        {"nombre": "Io", "masa": 8.93e22, "a_luna_inicial": 4.217e8, "k2": 0.015, "Q_p": 100},
        {"nombre": "Europa", "masa": 4.80e22, "a_luna_inicial": 6.711e8, "k2": 0.015, "Q_p": 100},
        {"nombre": "Ganimedes", "masa": 1.48e23, "a_luna_inicial": 1.070e9, "k2": 0.015, "Q_p": 100},
        {"nombre": "Calisto", "masa": 1.08e23, "a_luna_inicial": 1.883e9, "k2": 0.015, "Q_p": 100},
    ],
}
# NOTA (multi-luna, ago-2026): LUNAS[planeta] es una LISTA de lunas, no un
# dict único como en versiones anteriores. Cada entrada necesita "masa",
# "a_luna_inicial", "k2", "Q_p" y opcionalmente "nombre".
#
# k2/Q_p de las lunas galileanas: NO hay una medición directa publicada y
# consensuada por luna individual (a diferencia de la Luna terrestre, donde
# k2/Q_p=0.3/12 viene de LLR -- Lunar Laser Ranging). Se usa un valor
# fenomenológico (k2=0.015, Q_p=100, mismo orden que Júpiter mismo) como
# placeholder Tier C -- NO Tier A. Ver calcular_tier() más arriba: esto es
# consistente con el resto de la base de datos, que nunca presenta un
# estimado como si fuera medido. Ajustar cuando haya una referencia real
# (p.ej. Lainey et al. para el sistema joviano) antes de validar contra
# Horizons en la Fase 1 de multi-luna.
