# ===================================================================
# licencia.py
# Verificación de licencia para MHD-INT Standard/Pro.
# Licencia: Comercial propietaria (NO forma parte del repo público AGPL).
#
# CÓMO FUNCIONA:
# - Roney firma cada licencia offline con generar_licencia.py (queda en
#   su computadora, junto a la clave PRIVADA -- ninguno de los dos viaja
#   con el .exe).
# - Este archivo solo tiene la clave PÚBLICA embebida. Con eso alcanza
#   para VERIFICAR una firma, pero es matemáticamente imposible generar
#   una firma nueva a partir de ella -- así que aunque alguien lea este
#   código fuente completo (viene con el .exe, no se puede ocultar del
#   todo), no puede fabricar una licencia propia.
# - Lo único que se puede hacer sin la clave privada es COPIAR un
#   license.json ya válido y compartirlo -- eso este mecanismo no lo
#   evita (ningún sistema de licencia offline lo evita del todo). Sí
#   deja trazabilidad: el nombre/email del comprador original queda
#   dentro del propio archivo y se puede mostrar en la app y en los
#   reportes exportados (ver nota de watermark más abajo).
#
# QUÉ NO HACE (a propósito, para no prometer de más):
# - No llama a ningún servidor -- funciona sin internet. Por lo tanto
#   no puede "revocar" una licencia ya emitida y filtrada.
# - No ata la licencia a una máquina específica. Se puede agregar
#   (hash de hardware) si en algún momento se decide que vale la pena
#   la fricción/soporte extra que eso implica.
# ===================================================================

import json
import base64
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

# ---------------------------------------------------------------------
# Clave PÚBLICA de Solaris Core. Reemplazar por la real generada con
# generar_llaves.py antes del release comercial -- esta es de ejemplo.
# ---------------------------------------------------------------------
CLAVE_PUBLICA_PEM = b"""-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAETEKGm7aWFci4HTOFMKWYZQcVeXJX
1NOS88ODsS4RHrJswOlncc70niXV0hvKgweCpSqTON+IkPT4F3w7oWq6jQ==
-----END PUBLIC KEY-----
"""

NIVELES_VALIDOS = ("STANDARD", "PRO")

# Rutas donde se busca license.json, en orden. La primera es la normal
# (junto al .exe/script); la segunda cubre el caso de correrlo con
# "python app_streamlit_pro.py" desde otra carpeta durante desarrollo.
RUTAS_BUSQUEDA = (
    Path.cwd() / "license.json",
    Path(__file__).resolve().parent / "license.json",
)


class LicenciaInvalida(Exception):
    """Se usa para cualquier motivo de rechazo -- el detalle exacto se
    guarda en el mensaje, pero la UI solo muestra un texto genérico
    (ver app_streamlit_pro.py) para no darle a un atacante pistas de
    qué parte falló."""


def _reconstruir_mensaje_firmado(datos: dict) -> bytes:
    """Debe ser BYTE A BYTE lo mismo que arma generar_licencia.py al
    firmar: mismas claves, mismo sort_keys, mismos separators. Si algo
    de esto cambia de un lado sin cambiar del otro, TODAS las licencias
    ya emitidas dejan de validar."""
    datos_sin_firma = {k: v for k, v in datos.items() if k != "firma"}
    return json.dumps(datos_sin_firma, sort_keys=True, separators=(",", ":")).encode()


def _cargar_clave_publica():
    return serialization.load_pem_public_key(CLAVE_PUBLICA_PEM)


def verificar_licencia(nivel_requerido: str, ruta_license: Path | None = None) -> dict:
    """
    Verifica la licencia y devuelve el dict de datos (comprador, email,
    nivel, emitida, valido_hasta) si es válida. Lanza LicenciaInvalida
    en cualquier otro caso -- sin excepción no controlada, para que el
    caller siempre pueda mostrar un mensaje ordenado.
    """
    rutas = (ruta_license,) if ruta_license else RUTAS_BUSQUEDA
    ruta_encontrada = next((r for r in rutas if r and r.exists()), None)

    if ruta_encontrada is None:
        raise LicenciaInvalida("No se encontró license.json junto a la aplicación.")

    try:
        datos = json.loads(ruta_encontrada.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise LicenciaInvalida(f"license.json ilegible: {exc}") from exc

    if "firma" not in datos:
        raise LicenciaInvalida("license.json sin campo 'firma'.")

    firma = base64.b64decode(datos["firma"])
    mensaje = _reconstruir_mensaje_firmado(datos)

    try:
        _cargar_clave_publica().verify(firma, mensaje, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as exc:
        raise LicenciaInvalida("Firma inválida -- el archivo fue alterado o no es genuino.") from exc

    if datos.get("nivel") not in NIVELES_VALIDOS:
        raise LicenciaInvalida(f"Nivel de licencia desconocido: {datos.get('nivel')!r}.")

    # PRO puede correr contenido de Standard; Standard no puede abrir Pro.
    orden_nivel = {"STANDARD": 0, "PRO": 1}
    if orden_nivel[datos["nivel"]] < orden_nivel[nivel_requerido]:
        raise LicenciaInvalida(
            f"Esta licencia es {datos['nivel']}, pero esta build requiere {nivel_requerido}."
        )

    valido_hasta = datos.get("valido_hasta")
    if valido_hasta:
        fecha_limite = datetime.fromisoformat(valido_hasta)
        if fecha_limite.tzinfo is None:
            fecha_limite = fecha_limite.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > fecha_limite:
            raise LicenciaInvalida(f"Licencia vencida el {valido_hasta}.")

    return datos
