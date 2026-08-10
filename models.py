from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import numpy as np
import json

def a_nativo(valor):
    if hasattr(valor, "item"):
        return valor.item()
    return valor

@dataclass
class SerieTemporal:
    tiempos: List[float] = field(default_factory=list)
    a_ua: List[float] = field(default_factory=list)
    w_p: List[float] = field(default_factory=list)
    B_p_gauss: List[float] = field(default_factory=list)
    E_p: List[float] = field(default_factory=list)
    R_m_norm: List[float] = field(default_factory=list)
    tau_mag: List[float] = field(default_factory=list)
    tiempo_migracion: List[float] = field(default_factory=list)
    e: List[float] = field(default_factory=list)
    Q_tidal_watts: List[float] = field(default_factory=list)
    a_luna_ua: List[float] = field(default_factory=list)
    # ========= NUEVOS CAMPOS v4.2 (nucleo termico) =========
    T_cmb_K: List[float] = field(default_factory=list)
    B_gen_gauss: List[float] = field(default_factory=list)
    Rm_num: List[float] = field(default_factory=list)
    q_conv: List[float] = field(default_factory=list)
    # ========= NUEVOS CAMPOS v5.0 (atmosfera) =========
    M_atm_kg: List[float] = field(default_factory=list)
    atm_perdida: List[bool] = field(default_factory=list)
    # ========= NUEVO v5.1 (oblicuidad) =========
    eps_deg: List[float] = field(default_factory=list)
    def __len__(self): return len(self.tiempos)

CAMPOS_ESCALARES_FLOAT = [
    "a_inicial_ua", "a_final_ua", "w_inicial", "w_final",
    "B_inicial_gauss", "B_final_gauss", "P_rot_inicial_dias", "P_rot_final_dias",
    "E_p_final", "R_m_norm_final", "tau_mag_final", "tiempo_migracion_final",
    "e_inicial", "e_final", "Q_tidal_final_watts",
    "a_luna_inicial_ua", "a_luna_final_ua", "recesion_lunar_cm_anio",
    # ========= NUEVO v4.2 (nucleo termico) =========
    "T_cmb_final_K", "B_gen_final_gauss", "Rm_final", "q_conv_final",
    # ========= NUEVO v5.0 (atmosfera) =========
    "M_atm_final_kg",
    # ========= NUEVO v5.1 (oblicuidad) =========
    "eps_final_deg",
]
CAMPOS_ESCALARES_BOOL = ["campo_protegido", "se_estrello", "atm_perdida", "eps_conocido"]

@dataclass
class ResultadoSimulacion:
    nombre_planeta: str
    a_inicial_ua: float
    a_final_ua: float
    w_inicial: float
    w_final: float
    B_inicial_gauss: float
    B_final_gauss: float
    P_rot_inicial_dias: float
    P_rot_final_dias: float
    E_p_final: float
    R_m_norm_final: float
    tau_mag_final: float
    tiempo_migracion_final: float
    campo_protegido: bool
    se_estrello: bool
    e_inicial: float = 0.0
    e_final: float = 0.0
    Q_tidal_final_watts: float = 0.0
    a_luna_inicial_ua: float = 0.0
    a_luna_final_ua: float = 0.0
    recesion_lunar_cm_anio: float = 0.0
    # ========= NUEVO v4.2 (nucleo termico) =========
    T_cmb_final_K: float = 0.0
    B_gen_final_gauss: float = 0.0
    Rm_final: float = 0.0
    q_conv_final: float = 0.0
    # ========= NUEVO v5.0 (atmosfera) =========
    M_atm_final_kg: float = 0.0
    atm_perdida: bool = False
    # ========= NUEVO v5.1 (oblicuidad) =========
    eps_final_deg: float = 0.0
    eps_conocido: bool = False
    serie: Optional[SerieTemporal] = None
    error: Optional[str] = None

    def __post_init__(self):
        for campo in CAMPOS_ESCALARES_FLOAT:
            setattr(self, campo, float(a_nativo(getattr(self, campo))))
        for campo in CAMPOS_ESCALARES_BOOL:
            setattr(self, campo, bool(a_nativo(getattr(self, campo))))

    def es_valido(self) -> bool:
        return self.error is None

    def tiene_serie(self) -> bool:
        return self.serie is not None and len(self.serie) > 0

    def resumen_dict(self) -> dict:
        d = asdict(self)
        d.pop("serie", None)
        return d
