from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
from PIL import Image as PILImage
from skimage.morphology import skeletonize
import tflite_runtime.interpreter as tflite

# Configuracion del modelo
DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "assets" / "models" / "MathSymbols_Optimized1.tflite"

# Diccionario de clases utilizado por el modelo
CLASS_INDICES: Dict[str, int] = {
    "(": 0,
    ")": 1,
    "+": 2,
    "0": 3,
    "1": 4,
    "2": 5,
    "3": 6,
    "4": 7,
    "5": 8,
    "6": 9,
    "7": 10,
    "8": 11,
    "9": 12,
    "a": 13,
    "c": 14,
    "n": 15,
    "s": 16,
    "t": 17,
    "d": 18,
    "e": 19,
    "pi": 20,
    "x": 21,
    "y": 22,
    "z": 23,
}
CLASS_INDICES_INVERSE: Dict[int, str] = {v: k for k, v in CLASS_INDICES.items()}


@dataclass
class SymbolPrediction:
    index: int
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    original_crop: np.ndarray
    processed_crop: np.ndarray
    label: str
    source: str


@dataclass
class PipelineResult:
    raw_sequence: List[str]
    centers: List[Tuple[int, int]]
    raices_centros: List[Dict[int, Sequence[Tuple[int, int]]]]
    symbol_predictions: List[SymbolPrediction]
    debug: Dict[str, Any] = field(default_factory=dict)


def cargar_modelo(model_path: Optional[Path] = None) -> tflite.Interpreter:
    """
    Cargar el modelo TensorFlow Lite (.tflite) desde la ruta indicada.
    """
    path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en: {path}\n"
            "Coloca el archivo .tflite en esa ruta o proporciona una ruta valida."
        )

    interpreter = tflite.Interpreter(model_path=str(path))
    interpreter.allocate_tensors()
    return interpreter


def DeteccionRaiz(
    x: int,
    y: int,
    w: int,
    h: int,
    centros: Sequence[Tuple[int, int]],
    indice_actual: int,
) -> Tuple[bool, List[Tuple[int, int]]]:
    centrosdentro: List[Tuple[int, int]] = []
    raiz = False
    for i, centro in enumerate(centros):
        if i == indice_actual:
            continue
        x1, y1 = centro
        if x < x1 < x + w and y < y1 < y + h:
            centrosdentro.append(centro)
            raiz = True
    return raiz, centrosdentro


def tomartrazosygenerarcontornos(img: np.ndarray) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]], np.ndarray]:
    if len(img.shape) == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    imagenes: List[np.ndarray] = []
    posiciones: List[Tuple[int, int, int, int]] = []

    for cnt in contours:
        mask = np.zeros_like(thresh)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        trazo_mascara = cv2.bitwise_and(thresh, thresh, mask=mask)
        trazo_final = cv2.bitwise_not(trazo_mascara)
        x, y, w, h = cv2.boundingRect(cnt)
        recorte = trazo_final[y : y + h, x : x + w]
        imagenes.append(recorte)
        posiciones.append((x, y, w, h))

    return imagenes, posiciones, thresh


def CrearContornos(imagen: np.ndarray) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]], List[np.ndarray], np.ndarray, np.ndarray]:
    imagenes_procesadas, posiciones_procesadas, umbralizada = tomartrazosygenerarcontornos(imagen)
    contornos_originales, _ = cv2.findContours(umbralizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return imagenes_procesadas, posiciones_procesadas, contornos_originales, imagen, umbralizada


def PonerFondoBlanco(digito: np.ndarray, w: int, h: int) -> PILImage.Image:
    mayorlado = max(w, h)
    imagen_fondo = PILImage.new("L", (mayorlado, mayorlado), "white")
    imagen_encima = PILImage.fromarray(digito)
    posicion_x = (imagen_fondo.width - imagen_encima.width) // 2
    posicion_y = (imagen_fondo.height - imagen_encima.height) // 2
    imagen_fondo.paste(imagen_encima, (posicion_x, posicion_y))
    return imagen_fondo


def RedimensionarYEngrosar(digito: np.ndarray, tamaño: int = 45) -> np.ndarray:
    imagen_pil = PILImage.fromarray(digito)
    imagen_redimensionada = imagen_pil.resize((tamaño, tamaño), resample=PILImage.LANCZOS)
    imagen_np = np.array(imagen_redimensionada)

    _, binaria = cv2.threshold(imagen_np, 200, 255, cv2.THRESH_BINARY)
    invertida = cv2.bitwise_not(binaria)
    binaria_bool = invertida > 0
    skel = skeletonize(binaria_bool)
    esqueleto_img = (skel * 255).astype(np.uint8)

    grosor = 1
    if grosor > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grosor, grosor))
        engrosado = cv2.dilate(esqueleto_img, kernel)
    else:
        engrosado = esqueleto_img.copy()

    _, engrosado = cv2.threshold(engrosado, 127, 255, cv2.THRESH_BINARY)
    resultado = cv2.bitwise_not(engrosado)
    return resultado


def ProcesarContornos(
    contornos_originales: Sequence[np.ndarray],
    imagen: np.ndarray,
    imagenes_procesadas: Sequence[np.ndarray],
    posiciones_procesadas: Sequence[Tuple[int, int, int, int]],
) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]], List[Tuple[int, int]], List[Tuple[np.ndarray, Tuple[int, int, int, int]]]]:
    digitos_originales: List[np.ndarray] = []
    posiciones_originales: List[Tuple[int, int, int, int]] = []
    centros_originales: List[Tuple[int, int]] = []
    lista_digitos_procesados: List[Tuple[np.ndarray, Tuple[int, int, int, int]]] = []

    for i, contorno in enumerate(contornos_originales):
        x, y, w, h = cv2.boundingRect(contorno)
        recorte = imagen[y : y + h, x : x + w]
        posiciones_originales.append((x, y, w, h))
        digitos_originales.append(recorte)
        digitobueno = imagenes_procesadas[i]

        centro_x = x + w // 2
        centro_y = y + h // 2

        imagen_fondo = PonerFondoBlanco(digitobueno, posiciones_procesadas[i][2], posiciones_procesadas[i][3])
        imagen_np = np.array(imagen_fondo)

        digito_redimensionado = RedimensionarYEngrosar(imagen_np, tamaño=45)

        centros_originales.append((centro_x, centro_y))
        lista_digitos_procesados.append((digito_redimensionado, (x, y, w, h)))

    indices_raices: List[int] = []
    for i, contorno in enumerate(contornos_originales):
        x, y, w, h = cv2.boundingRect(contorno)
        raiz, dentro = DeteccionRaiz(x, y, w, h, centros_originales, i)
        if raiz:
            centros_originales[i] = (x, y + h // 2)
            indices_raices.append(i)

    return digitos_originales, posiciones_originales, centros_originales, lista_digitos_procesados


def ordenar_ecuacion(
    digitos_originales: Sequence[np.ndarray],
    centros: Sequence[Tuple[int, int]],
    lista_digitos: Sequence[Tuple[np.ndarray, Tuple[int, int, int, int]]],
) -> Tuple[List[np.ndarray], List[Tuple[int, int]], List[Tuple[np.ndarray, Tuple[int, int, int, int]]]]:
    matrix = [(digitos_originales[i], centros[i], lista_digitos[i]) for i in range(len(centros))]
    sorted_matrix = sorted(matrix, key=lambda x: x[1][0])
    imagenes_sort = [sorted_matrix[i][0] for i in range(len(sorted_matrix))]
    centros_sorted = [sorted_matrix[i][1] for i in range(len(sorted_matrix))]
    lista_digitos_sorted = [sorted_matrix[i][2] for i in range(len(sorted_matrix))]
    return imagenes_sort, centros_sorted, lista_digitos_sorted


def DeteccionDivResta(
    x: int,
    y: int,
    w: int,
    h: int,
    centros: Sequence[Tuple[int, int]],
    i: int,
) -> Tuple[bool, bool]:
    ancho = x + w
    arriba = False
    abajo = False

    if w > 7 * h:
        for j, (x1, y1) in enumerate(centros):
            if x < x1 < ancho:
                if y1 < y:
                    arriba = True
                elif y1 > y:
                    abajo = True

        if arriba and abajo:
            return True, False
        return False, True

    return False, False


def DeteccionPunto(digito: np.ndarray, umbral: float = 0.2) -> bool:
    black_pixels = np.sum(digito < 0.5)
    total_pixels = digito.size
    black_ratio = black_pixels / total_pixels if total_pixels else 0.0
    return black_ratio > umbral


def DeteccionComa(h: int, w: int) -> bool:
    return h < 20 and w < 20


def detectarsimbolesespeciales(
    lista_digitos_sorted: Sequence[Tuple[np.ndarray, Tuple[int, int, int, int]]],
    posiciones_originales: Sequence[Tuple[int, int, int, int]],
    centros_sorted: Sequence[Tuple[int, int]],
) -> Tuple[List[int], List[int], List[int], List[int], List[int], List[Dict[int, Sequence[Tuple[int, int]]]]]:
    diviciones: List[int] = []
    puntos: List[int] = []
    raizes: List[int] = []
    restas: List[int] = []
    comas: List[int] = []
    diccionarioraizes: List[Dict[int, Sequence[Tuple[int, int]]]] = []

    for i, (digito_redimensionado, (x, y, w, h)) in enumerate(lista_digitos_sorted):
        raiz, centrosdentro = DeteccionRaiz(x, y, w, h, centros_sorted, i)
        if raiz:
            raizes.append(i)
            diccionarioraizes.append({i: centrosdentro})

        fraccion, resta = DeteccionDivResta(x, y, w, h, centros=centros_sorted, i=i)
        if fraccion:
            diviciones.append(i)
        if resta:
            restas.append(i)

        if DeteccionPunto(digito_redimensionado):
            puntos.append(i)

        if DeteccionComa(h, w):
            comas.append(i)

    return diviciones, puntos, raizes, restas, comas, diccionarioraizes


def Ai(class_indices_inverse: Dict[int, str], img_array: np.ndarray, interpreter: tflite.Interpreter) -> str:
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    img_array = np.expand_dims(img_array, axis=-1)
    img_array = np.expand_dims(img_array, axis=0)

    interpreter.set_tensor(input_details[0]["index"], img_array)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]["index"])
    predicted_class = int(np.argmax(output_data))
    return class_indices_inverse[predicted_class]


def run_pipeline(
    image: np.ndarray,
    interpreter: Optional[tflite.Interpreter] = None,
    collect_debug: bool = False,
    model_path: Optional[Path] = None,
) -> PipelineResult:
    """
    Ejecuta el pipeline completo de deteccion y clasificacion.
    """
    if interpreter is None:
        interpreter = cargar_modelo(model_path=model_path)

    imagenes_procesadas, posiciones_procesadas, contornos_originales, imagen_base, umbralizada = CrearContornos(image)

    digitos_originales, posiciones_originales, centros_originales, lista_digitos_procesados = ProcesarContornos(
        contornos_originales, imagen_base, imagenes_procesadas, posiciones_procesadas
    )

    imagenes_sort, centros_sorted, lista_digitos_sorted = ordenar_ecuacion(
        digitos_originales, centros_originales, lista_digitos_procesados
    )

    diviciones, puntos, raizes, restas, comas, raizes_centros = detectarsimbolesespeciales(
        lista_digitos_sorted, posiciones_originales, centros_sorted
    )

    cadena: List[str] = []
    symbol_predictions: List[SymbolPrediction] = []

    for i, (digito_redimensionado, bbox) in enumerate(lista_digitos_sorted):
        if i in diviciones:
            label = "div"
            source = "division"
        elif i in restas:
            label = "-"
            source = "minus"
        elif i in raizes:
            label = "q"
            source = "root"
        elif i in puntos:
            label = "*"
            source = "dot"
        elif i in comas:
            label = "."
            source = "comma"
        else:
            img_array = np.array(digito_redimensionado, dtype=np.float32) / 255.0
            label = Ai(CLASS_INDICES_INVERSE, img_array, interpreter)
            source = "model"

        cadena.append(label)
        symbol_predictions.append(
            SymbolPrediction(
                index=i,
                bbox=bbox,
                center=centros_sorted[i],
                original_crop=imagenes_sort[i],
                processed_crop=digito_redimensionado,
                label=label,
                source=source,
            )
        )

    debug: Dict[str, Any] = {}
    if collect_debug:
        debug = {
            "imagenes_procesadas": imagenes_procesadas,
            "posiciones_procesadas": posiciones_procesadas,
            "contornos_originales": contornos_originales,
            "imagen_base": imagen_base,
            "umbralizada": umbralizada,
            "digitos_originales": digitos_originales,
            "posiciones_originales": posiciones_originales,
            "imagenes_sort": imagenes_sort,
            "diviciones": diviciones,
            "puntos": puntos,
            "raizes": raizes,
            "restas": restas,
            "comas": comas,
        }

    return PipelineResult(
        raw_sequence=cadena,
        centers=centros_sorted,
        raices_centros=raizes_centros,
        symbol_predictions=symbol_predictions,
        debug=debug,
    )


def ProduccionPredicciones(
    image: np.ndarray,
    interpreter: Optional[tflite.Interpreter] = None,
    model_path: Optional[Path] = None,
    collect_debug: bool = False,
):
    """
    Envoltura compatible con el codigo existente que devuelve los mismos valores
    que la version anterior de ProduccionPredicciones.
    """
    result = run_pipeline(
        image,
        interpreter=interpreter,
        collect_debug=collect_debug,
        model_path=model_path,
    )

    lista_digitos_sorted = [
        (symbol.processed_crop, symbol.bbox) for symbol in result.symbol_predictions
    ]

    if collect_debug:
        return (
            result.raw_sequence,
            lista_digitos_sorted,
            result.centers,
            result.raices_centros,
            result,
        )

    return result.raw_sequence, lista_digitos_sorted, result.centers, result.raices_centros
