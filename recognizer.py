"""
Funciones para ejecutar el pipeline de reconocimiento directamente desde una imagen.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from PIL import Image as PILImage

from digit_pipeline import ProduccionPredicciones
from strtraductor import (
    Organizarcadena,
    depurar_parentesis,
    depurar_trigonometria,
    exponentes,
    modificar_indices,
    raices,
)


def reconocer_expresion(image: PILImage.Image) -> Optional[str]:
    """
    Procesa una imagen PIL y devuelve la expresión matemática reconocida.
    """
    try:
        grayscale = image.convert("L")
        img_array = np.array(grayscale)

        cadena, sort_list, centros, _ = ProduccionPredicciones(img_array)

        cadena_organizada, indices = Organizarcadena(cadena, sort_list, centros)
        cadena_trig = depurar_trigonometria(cadena_organizada)
        indices_mod = modificar_indices(cadena_trig, indices)
        cadena_raices, indices_raices = raices(cadena_trig, indices_mod, sort_list, centros)
        cadena_sin_parentesis = depurar_parentesis(cadena_raices, indices_raices)
        cadena_final, _ = exponentes(cadena_sin_parentesis, indices_raices, sort_list, centros)

        expresion = (
            cadena_final.replace("¿", "(")
            .replace("?", ")")
            .replace("p", "π")
            .replace("r", "root")
            .replace("q", "sqrt")
            .replace("d", "/")
        )
        return expresion
    except Exception as exc:  # pragma: no cover
        print(f"❌ Error al reconocer la expresión: {exc}")
        return None
